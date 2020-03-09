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
from django import forms
from django.contrib import admin

from ensembl_dbcopy.models import Host, Group
from ensembl_production.admin import SuperUserAdmin


class HostRecordForm(forms.ModelForm):
    class Meta:
        exclude = ('auto_id',)


class GroupRecordForm(forms.ModelForm):
    class Meta:
        exclude = ('group_id',)


@admin.register(Host)
class HostItemAdmin(admin.ModelAdmin, SuperUserAdmin):

    form = HostRecordForm
    list_display = ('name', 'port', 'mysql_user', 'virtual_machine', 'mysqld_file_owner')
    fields = ('name', 'port', 'mysql_user', 'virtual_machine', 'mysqld_file_owner')
    search_fields = ('name', 'port', 'mysql_user', 'virtual_machine', 'mysqld_file_owner')


@admin.register(Group)
class GroupItemAdmin(admin.ModelAdmin, SuperUserAdmin):
    form = GroupRecordForm
    list_display = ('host_id', 'group_name')
    fields = ('host_id', 'group_name')
    search_fields = ('host_id', 'group_name')
