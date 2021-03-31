"""
.. See the NOTICE file distributed with this work for additional information
   regarding copyright ownership.
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import logging
import re

from django.db.models import fields

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.core.validators import RegexValidator, EmailValidator

from ensembl_dbcopy.api.views import get_database_set  # , get_engine
from ensembl_dbcopy.models import RequestJob, Group, Host, TargetHostGroup
from django.contrib.auth.models import User
from django.contrib.auth.models import Group as UserGroup
from collections import OrderedDict

logger = logging.getLogger(__name__)

COMMA_RE = re.compile(',+')


def _target_host_group(username):

    # get groups, current user belongs to 
    user_groups = [   each_group .name 
        for user_obj in User.objects.filter(username__contains=username).prefetch_related('groups').all()
        for each_group in user_obj.groups.all()
    ]

    #get all host user can copy  based on assigned group 
    user_hosts_ids = [ host.auto_id for host in Host.objects.filter(groups__group_name__in=user_groups) ]  
    
    #get all host names that target group contains
    target_host_dict = {} 
    for each_group in TargetHostGroup.objects.all():
        target_host_dict[each_group.target_group_name] = ''
        for each_host in each_group.target_host.all():
            target_host_dict[each_group.target_group_name] += each_host.name +':'+str(each_host.port)+','
            
     
    #get all the target group that has access to host from authgroup
    target_groups =  list(set([ (
                            target_host_dict[groups.target_group_name], 
                            groups.target_group_name
                            )  
                        for groups in TargetHostGroup.objects.filter(target_host__auto_id__in=user_hosts_ids) 
                    ]))
    target_groups.insert(0, ('', '--select target group--'))
    return target_groups


def _text_field_as_set(text):
    return set(filter(lambda x: x != '', text.split(',')))


def _apply_db_names_filter(db_names, all_db_names):
    if len(db_names) == 1:
        db_name = db_names.pop()
        filter_re = re.compile(db_name.replace('%', '.*').replace('_', '.'))
        return set(filter(filter_re.search, all_db_names))
    return db_names


class TrimmedCharField(forms.CharField):
    def to_python(self, value):
        value = super().to_python(value)
        if not value:
            return ''
        return COMMA_RE.sub(',', value.replace(' ', '').rstrip(','))


class ListFieldRegexValidator(RegexValidator):
    def __call__(self, value):
        elements = value.split(',')
        for element in elements:
            super().__call__(element)


class EmailListFieldValidator(EmailValidator):
    def __call__(self, value):
        elements = value.split(',')
        for element in elements:
            super().__call__(element)


class SubmitForm(forms.ModelForm):
    class Meta:
        model = RequestJob
        exclude = ('job_id', 'tgt_directory')
        # fields = ["src_host","src_incl_db","src_skip_db","src_incl_tables",
        #             "src_skip_tables","tgt_host","tgt_db_name", "skip_optimize",
        #             "email_list"]

    src_host = TrimmedCharField(
        label="Source Host ",
        help_text="host:port",
        max_length=2048,
        required=True,
        validators=[
            RegexValidator(
                regex="^[\w-]+:[0-9]{4}",
                message="Source Host should be formatted like this host:port"
            )
        ])
    tgt_host = TrimmedCharField(
        label="Target Hosts",
        help_text="Host1:port1,Host2:port2",
        max_length=2048,
        required=True,
        validators=[
            ListFieldRegexValidator(
                regex="^[\w-]+:[0-9]{4}",
                message="Target Hosts should be formatted like this host:port or host1:port1,host2:port2"
            )
        ])
    src_incl_db = TrimmedCharField(
        label="Databases to copy",
        help_text='db1,db2,.. or %variation_99% ',
        max_length=2048,
        required=False)
    src_skip_db = TrimmedCharField(
        label="Databases to exclude",
        help_text='db1,db2 or %mart%',
        max_length=2048,
        required=False)
    src_incl_tables = TrimmedCharField(
        label="Only Copy these tables",
        help_text='table1,table2,..',
        max_length=2048,
        required=False)
    src_skip_tables = TrimmedCharField(
        label="Skip these tables",
        help_text='table1,table2,..',
        max_length=2048,
        required=False)
    tgt_db_name = TrimmedCharField(
        label="Name of databases on Target Hosts",
        help_text='db1,db2,..',
        max_length=2048,
        required=False)
    email_list = TrimmedCharField(
        label="Email list",
        help_text='Comma separated list',
        max_length=2048,
        required=True,
        validators=[
            EmailListFieldValidator(
                message="Email list should contain one or more comma separated valid email addresses."
            )
        ])
    user = forms.CharField(
        widget=forms.HiddenInput())

    def _validate_db_skipping(self, src_skip_db_names, tgt_db_names):
        if src_skip_db_names and tgt_db_names:
            self.add_error('src_skip_db',
                           'Field "Names of databases on Target Host" is not empty. Consider clear it, or clear this field.')

    def _validate_db_renaming(self, src_dbs, tgt_dbs):
        if tgt_dbs:
            if len(tgt_dbs) != len(src_dbs):
                self.add_error('tgt_db_name',
                               "The number of databases to copy should match the number of databases renamed on target hosts")
            for dbname in src_dbs:
                if '%' in dbname:
                    self.add_error('tgt_db_name', "You can't rename a pattern")

    def _validate_source_and_target(self, src_host, tgt_hosts, src_dbs, src_skip_dbs, tgt_db_names):
        if src_host in tgt_hosts:
            hostname, port = src_host.split(':')
            try:
                present_dbs = get_database_set(hostname, port)
            except ValueError as e:
                raise forms.ValidationError('Invalid source hostname or port')
            src_names = present_dbs
            if src_dbs:
                src_names = _apply_db_names_filter(src_dbs, src_names)
            if src_skip_dbs:
                skip_names = _apply_db_names_filter(src_skip_dbs, present_dbs)
                src_names = src_names.difference(skip_names)

            if tgt_db_names:
                tgt_conflicts = tgt_db_names.intersection(src_names)
                if tgt_conflicts:
                    raise forms.ValidationError(
                        'Some source and target databases coincide. Please change conflicting target names')
            elif src_names:
                raise forms.ValidationError(
                    'Some source and target databases coincide. Please add target names or change sources')

    #  # Commented until this feature is enabled by DBAs
    #  def _validate_wipe_target(self, wipe_target, src_dbs, src_skip_dbs, tgt_hosts, tgt_db_names, src_incl_tables):
    #      src_db_names = src_dbs.difference(src_skip_dbs)
    #      new_db_names = tgt_db_names if tgt_db_names else src_db_names
    #      if (wipe_target is False) and (not src_incl_tables) and new_db_names:
    #          for tgt_host in tgt_hosts:
    #              hostname, port = tgt_host.split(':')
    #              try:
    #                  db_engine = get_engine(hostname, port)
    #              except RuntimeError as e:
    #                  self.add_error('tgt_host', 'Invalid host: {}'.format(tgt_host))
    #                  continue
    #              tgt_present_db_names = set(sa.inspect(db_engine).get_schema_names())
    #              if tgt_present_db_names.intersection(new_db_names):
    #                  field_name = 'tgt_db_name' if tgt_db_names else 'src_incl_db'
    #                  self.add_error(field_name,
    #                                 'One or more database names already present on the target. Consider enabling Wipe target option.')
    #                  break

    def _validate_user_permission(self, tgt_hosts):
        # Checking that user is allowed to copy to the target server.
        for tgt_host in tgt_hosts:
            hostname = tgt_host.split(':')[0]
            hosts = Host.objects.filter(name=hostname)
            if not hosts:
                self.add_error('tgt_host', hostname + " is not present in our system")
                return
            group = Group.objects.filter(host_id=hosts[0].auto_id)
            if group:
                host_groups = group.values_list('group_name', flat=True)
                user_groups = self.user.groups.values_list('name', flat=True)
                common_groups = set(host_groups).intersection(set(user_groups))
                if not common_groups:
                    self.add_error('tgt_host', "You are not allowed to copy to " + hostname)

    def clean(self):
        cleaned_data = super().clean()
        src_host = cleaned_data.get('src_host', '')
        # wipe_target = cleaned_data.get('wipe_target', False)
        # src_incl_tables = cleaned_data.get('src_incl_tables', '')
        tgt_hosts = _text_field_as_set(cleaned_data.get('tgt_host', ''))
        src_dbs = _text_field_as_set(cleaned_data.get('src_incl_db', ''))
        src_skip_dbs = _text_field_as_set(cleaned_data.get('src_skip_db', ''))
        tgt_db_names = _text_field_as_set(cleaned_data.get('tgt_db_name', ''))
        self._validate_db_skipping(src_skip_dbs, tgt_db_names)
        self._validate_db_renaming(src_dbs, tgt_db_names)
        self._validate_source_and_target(src_host, tgt_hosts, src_dbs, src_skip_dbs, tgt_db_names)
        # self._validate_wipe_target(wipe_target, src_dbs, src_skip_dbs, tgt_hosts, tgt_db_names, src_incl_tables)
        self._validate_user_permission(tgt_hosts)

    def __init__(self, *args, **kwargs):
        if 'initial' in kwargs and 'from_request_job' in kwargs['initial']:
            kwargs['instance'] = RequestJob.objects.get(pk=kwargs['initial']['from_request_job'])
        super(SubmitForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields["email_list"].initial = self.user.email
        self.fields["user"].initial = self.user.username
        self.helper.form_id = 'copy-job-form'
        self.helper.form_class = 'copy-job-form'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))

        target_host_group_list = _target_host_group(self.user.username)
        if len(target_host_group_list) > 1:
            tgt_group_host = forms.CharField(required=False)
            tgt_group_host.widget = forms.Select(choices=target_host_group_list,
                                                      
                                                    attrs={'onchange': "targetHosts()"}
                                                )
            tgt_group_host.label = 'Host Target Group'
            tgt_group_host.help_text="Select Group to autofill the target host"

            field_order = list(self.fields.items())
            field_order.insert(5, ("tgt_group_host", tgt_group_host ))
            self.fields = OrderedDict(field_order)


     
