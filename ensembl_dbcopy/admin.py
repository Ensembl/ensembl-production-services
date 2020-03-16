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
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter
from django.db.models import Count


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

class OverallStatusFilter(SimpleListFilter):
    title = 'status' # or use _('country') for translated title
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        status = set([s.overall_status for s in model_admin.model.objects.all()])
        return [(s, s) for s in status]

    def queryset(self, request, queryset):
        if self.value() == 'Failed':
            qs = queryset.filter(end_date__isnull=False,status__isnull=False)
            return qs.filter(transfer_logs__end_date__isnull=True).annotate(count_transfer=Count('transfer_logs')).filter(count_transfer__gt=0)
        elif self.value() == 'Complete':
            qs = queryset.filter(end_date__isnull=False,status__isnull=False)
            print(qs.filter(transfer_logs__end_date__isnull=False).annotate(count_transfer=Count('transfer_logs')))
            return qs.exclude(transfer_logs__end_date__isnull=True)
        elif self.value() == 'Running':
            qs = queryset.filter(end_date__isnull=True,status__isnull=True)
            return qs.annotate(count_transfer=Count('transfer_logs')).filter(count_transfer__gt=0)
        elif self.value() == 'Submitted':
            qs = queryset.filter(end_date__isnull=True,status__isnull=True)
            return qs.annotate(count_transfer=Count('transfer_logs')).filter(count_transfer=0)


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
    list_display = ('job_id', 'src_host', 'src_incl_db', 'src_skip_db', 'tgt_host', 'tgt_db_name', 'user', 'start_date', 'end_date', 'overall_status')
    list_filter = ('src_host','tgt_host', 'user', OverallStatusFilter)
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

    def overall_status(self, obj):
        return format_html(
            '<b class="field-overall_status {}">{}</b>',
            obj.overall_status,
            obj.overall_status,
        )

