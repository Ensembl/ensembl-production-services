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

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from ensembl_dbcopy.models import RequestJob, Group, Host


class SubmitForm(forms.ModelForm):
    class Meta:
        model = RequestJob
        exclude = ('job_id', 'tgt_directory')

    src_host = forms.CharField(
        label="Source Host (e.g: host:port)",
        max_length=2048,
        required=True)
    tgt_host = forms.CharField(
        label="Target Hosts (e.g: Host1:port1,Host2:port2)",
        max_length=2048,
        required=True)
    src_incl_db = forms.CharField(
        label="Databases to copy (e.g: db1,db2,.. or %variation_99% )",
        max_length=2048,
        required=False)
    src_skip_db = forms.CharField(
        label="Databases to exclude (e.g db1,db2 or %mart%)",
        max_length=2048,
        required=False)
    src_incl_tables = forms.CharField(
        label="Only Copy these tables (e.g: table1,table2,..):",
        max_length=2048,
        required=False)
    src_skip_tables = forms.CharField(
        label="Skip these tables (e.g: table1,table2)",
        max_length=2048,
        required=False)
    tgt_db_name = forms.CharField(
        label="Name of databases on Target Hosts (e.g: db1,db2)",
        max_length=2048,
        required=False)
    email_list = forms.CharField(
        label="Email list",
        max_length=2048,
        required=True)
    user = forms.CharField(
        widget=forms.HiddenInput())

    def clean_src_host(self):
        src_host_pattern = re.compile("^.+:[0-9]{4}")
        data = self.cleaned_data['src_host']
        if not src_host_pattern.fullmatch(data):
            raise forms.ValidationError("Source Host should be formatted like this host:port")
        return data

    def clean_tgt_host(self):
        tgt_host_pattern = re.compile("^(.+:[0-9]{4},?)+")
        data = self.cleaned_data['tgt_host'].rstrip(',')
        if not tgt_host_pattern.fullmatch(data):
            raise forms.ValidationError(
                "Source Host should be formatted like this host:port or host1:port1,host2:port2")
        # Checking that user is allowed to copy to the target server.
        for host in self.cleaned_data['tgt_host'].rstrip(',').split(','):
            cleaned_host = host.split(':')[0]
            host_queryset = Host.objects.filter(name=cleaned_host)
            group = Group.objects.filter(host_id=host_queryset[0].auto_id)
            if group:
                host_groups = group.values_list('group_name', flat=True)
                user_groups = self.user.groups.values_list('name', flat=True)
                common_groups = set(host_groups).intersection(set(user_groups))
                if not common_groups:
                    raise forms.ValidationError("You are not allowed to copy to " + cleaned_host)
        return data

    def clean_src_incl_db(self):
        data = self.cleaned_data['src_incl_db'].rstrip(',')
        return data

    def clean_src_skip_db(self):
        data = self.cleaned_data['src_skip_db'].rstrip(',')
        return data

    def clean_src_incl_tables(self):
        data = self.cleaned_data['src_incl_tables'].rstrip(',')
        return data

    def clean_src_skip_tables(self):
        data = self.cleaned_data['src_skip_tables'].rstrip(',')
        return data

    def clean_email_list(self):
        email_list_pattern = re.compile("^(.+@.+,?)+")
        data = self.cleaned_data['email_list'].rstrip(',')
        if not email_list_pattern.fullmatch(data):
            raise forms.ValidationError(
                "Email list should be formatted like this joe.bloggs@ebi.ac.uk or joe.bloggs@ebi.ac.uk,toto@ebi.ac.uk")
        return data

    def clean_tgt_db_name(self):
        tgt_db_name = self.cleaned_data.get('tgt_db_name', '')
        src_incl_db = self.cleaned_data.get('src_incl_db', '')
        if tgt_db_name:
            if tgt_db_name.count(',') != src_incl_db.count(','):
                raise forms.ValidationError(
                    "The number of databases to copy should match the number of databases renamed on target hosts")
            if '%' in src_incl_db:
                raise forms.ValidationError(
                    "You can't rename a pattern")
        return tgt_db_name


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


class HostRecordForm(forms.ModelForm):
    class Meta:
        exclude = ('auto_id',)


class GroupRecordForm(forms.ModelForm):
    class Meta:
        exclude = ('group_id',)