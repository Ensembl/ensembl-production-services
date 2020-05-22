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
from django.contrib.admin import SimpleListFilter
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models import F
from django.utils.html import format_html

from ensembl_dbcopy.forms import SubmitForm, GroupForm
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


class OverallStatusFilter(SimpleListFilter):
    title = 'status'  # or use _('country') for translated title
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        status = set([s.overall_status for s in model_admin.model.objects.all()])
        return [(s, s) for s in status]

    def queryset(self, request, queryset):
        if self.value() == 'Failed':
            qs = queryset.filter(end_date__isnull=False, status__isnull=False)
            return qs.filter(transfer_logs__end_date__isnull=True).annotate(
                count_transfer=Count('transfer_logs')).filter(count_transfer__gt=0)
        elif self.value() == 'Complete':
            qs = queryset.filter(end_date__isnull=False, status__isnull=False)
            print(qs.filter(transfer_logs__end_date__isnull=False).annotate(count_transfer=Count('transfer_logs')))
            return qs.exclude(transfer_logs__end_date__isnull=True)
        elif self.value() == 'Running':
            qs = queryset.filter(end_date__isnull=True, status__isnull=True)
            return qs.annotate(count_transfer=Count('transfer_logs')).filter(count_transfer__gt=0)
        elif self.value() == 'Submitted':
            qs = queryset.filter(end_date__isnull=True, status__isnull=True)
            return qs.annotate(count_transfer=Count('transfer_logs')).filter(count_transfer=0)


class UserFilter(SimpleListFilter):
    """
    This filter will always return a subset of the instances in a Model, either filtering by the
    user choice or by a default value.
    """
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'user'
    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'user'
    default_value = None

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        list_of_users = []
        queryset = model_admin.model.objects.all()
        for q in queryset:
            if q.user:
                list_of_users.append(
                    (str(q.user), q.user)
                )
        return sorted(list(set(list_of_users+[("all", "all"), ])), key=lambda tp: tp[1])

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value to decide how to filter the queryset.
        if self.value():
            if self.value() != "all":
                return queryset.filter(user=self.value())
            else:
                return queryset.all()
        return queryset.filter(user=request.user)


@admin.register(Group)
class GroupItemAdmin(admin.ModelAdmin, SuperUserAdmin):
    form = GroupForm #GroupRecordForm
    add_form_template = "admin/dbcopy/multiselect.html" 
    list_display = ('host_id', 'group_name')
    fields = ('host_id', 'group_name')
    search_fields = ('group_name', 'host_id__auto_id')
 


@admin.register(RequestJob)
class RequestJobAdmin(admin.ModelAdmin):
    class Media:
        js = ('js/multiselect.js',)
        css = {
            'all': ('css/db_copy.css',)
        }

    form = SubmitForm
    add_form_template = "admin/dbcopy/submit.html"
    change_form_template = "admin/dbcopy/detail.html"
    list_display = ('job_id', 'src_host', 'src_incl_db', 'src_skip_db', 'tgt_host', 'tgt_db_name', 'user',
                    'start_date', 'end_date', 'overall_status')
    list_filter = ('src_host', 'tgt_host', UserFilter, OverallStatusFilter)
    ordering = ('start_date',)

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_module_permission(self, request):
        return request.user.is_staff

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
            '<div class="overall_status {}">{}</div>',
            obj.overall_status,
            obj.overall_status,
        )
