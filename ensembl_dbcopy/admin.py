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
from django.core.paginator import Paginator
from django.db.models import F

from ensembl_dbcopy.forms import SubmitForm
from ensembl_dbcopy.models import Host, Group, RequestJob
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


@admin.register(RequestJob)
class RequestJobAdmin(admin.ModelAdmin):
    form = SubmitForm
    add_form_template = "admin/dbcopy/submit.html"
    change_form_template = "admin/dbcopy/detail.html"
    # TODO might need some light updates
    list_display = ('job_id', 'src_host', 'tgt_host', 'user', 'status')
    list_filter = ('tgt_host', 'user', 'status')
    ordering = ('start_date', )
    # TODO add filters as needed
    # TODO add specific filters: group ? owner ? all ? see IsDisplayableFilter if needed
    # def get_queryset(self, request):
    #    queryset = super().get_queryset(request)
    #    return queryset.filter(user=request.user.username)

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff

    def has_module_permission(self, request):
        return request.user.is_staff

    class Media:
        js = ('js/multiselect.js', )
        css = {
            'all': ('css/db_copy.css',)
        }

    def has_delete_permission(self, request, obj=None):
        # Allow delete only for superusers
        return request.user.is_superuser

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.user = request.user
        return form

    def change_view(self, request, object_id, form_url='', extra_context=None):
        context = extra_context or {}
        transfers_logs = self.get_object(request, object_id).transfer_logs
        paginator = Paginator(transfers_logs.order_by(F('end_date').desc(nulls_first=True)), 30)
        page_number = request.GET.get('page', 1)
        page = paginator.page(page_number)
        context['transfer_logs'] = page
        return super().change_view(request, object_id, form_url, context)





