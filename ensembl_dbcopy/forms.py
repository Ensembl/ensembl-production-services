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
import re

import logging

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.core.validators import RegexValidator, EmailValidator
import sqlalchemy as sa

from ensembl_dbcopy.models import RequestJob, Group, Host
from ensembl_dbcopy.api.views import get_database_set #, get_engine


logger = logging.getLogger(__name__)


COMMA_RE = re.compile(',+')


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

    src_host = TrimmedCharField(
        label="Source Host (e.g: host:port)",
        max_length=2048,
        required=True,
        validators=[
            RegexValidator(
                regex="^[\w-]+:[0-9]{4}",
                message="Source Host should be formatted like this host:port"
            )
        ])
    tgt_host = TrimmedCharField(
        label="Target Hosts (e.g: Host1:port1,Host2:port2)",
        max_length=2048,
        required=True,
        validators=[
            ListFieldRegexValidator(
                regex="^[\w-]+:[0-9]{4}",
                message="Target Hosts should be formatted like this host:port or host1:port1,host2:port2"
            )
        ])
    src_incl_db = TrimmedCharField(
        label="Databases to copy (e.g: db1,db2,.. or %variation_99% )",
        max_length=2048,
        required=False)
    src_skip_db = TrimmedCharField(
        label="Databases to exclude (e.g db1,db2 or %mart%)",
        max_length=2048,
        required=False)
    src_incl_tables = TrimmedCharField(
        label="Only Copy these tables (e.g: table1,table2,..):",
        max_length=2048,
        required=False)
    src_skip_tables = TrimmedCharField(
        label="Skip these tables (e.g: table1,table2)",
        max_length=2048,
        required=False)
    tgt_db_name = TrimmedCharField(
        label="Name of databases on Target Hosts (e.g: db1,db2)",
        max_length=2048,
        required=False)
    email_list = TrimmedCharField(
        label="Email list",
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
            if tgt_db_names:
                tgt_conflicts = tgt_db_names.intersection(present_dbs)
                if tgt_conflicts:
                    raise forms.ValidationError('Some source and target databases coincide. Please change conflicting target names')
            else:
                src_names = src_dbs if src_dbs else present_dbs
                skip_names = _apply_db_names_filter(src_skip_dbs, present_dbs)
                db_names = _apply_db_names_filter(src_names, present_dbs).difference(skip_names)
                if db_names:
                    raise forms.ValidationError('Some source and target databases coincide. Please add target names or change sources')

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
        for host in tgt_hosts:
            cleaned_host = host.split(':')[0]
            host_queryset = Host.objects.filter(name=cleaned_host)
            group = Group.objects.filter(host_id=host_queryset[0].auto_id)
            if group:
                host_groups = group.values_list('group_name', flat=True)
                user_groups = self.user.groups.values_list('name', flat=True)
                common_groups = set(host_groups).intersection(set(user_groups))
                if not common_groups:
                    self.add_error('tgt_host', "You are not allowed to copy to " + cleaned_host)

    def clean(self):
        cleaned_data = super().clean()
        src_host = cleaned_data['src_host']
        # wipe_target = cleaned_data['wipe_target']
        src_incl_tables = cleaned_data['src_incl_tables']
        tgt_hosts = _text_field_as_set(cleaned_data['tgt_host'])
        src_dbs = _text_field_as_set(cleaned_data['src_incl_db'])
        src_skip_dbs = _text_field_as_set(cleaned_data['src_skip_db'])
        tgt_db_names = _text_field_as_set(cleaned_data['tgt_db_name'])
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
