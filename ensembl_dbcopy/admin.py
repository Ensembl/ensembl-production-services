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
from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.utils import model_ngettext
from django.contrib.auth.models import Group as UsersGroup
from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from django.utils.html import format_html

from ensembl_dbcopy.forms import SubmitForm
from ensembl_dbcopy.models import Host, RequestJob, Group
from ensembl_production.admin import SuperUserAdmin


class GroupInlineForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('group_name',)

    group_name = forms.ModelChoiceField(queryset=UsersGroup.objects.all().order_by('name'), to_field_name='name',
                                        empty_label='Please Select', required=True)


class GroupInline(admin.TabularInline):
    model = Group
    extra = 1
    form = GroupInlineForm
    fields = ('group_name',)
    verbose_name = "Group restriction"
    verbose_name_plural = "Group restrictions"


@admin.register(Host)
class HostItemAdmin(admin.ModelAdmin, SuperUserAdmin):
    class Media:
        css = {
            'all': ('css/db_copy.css',)
        }

    # form = HostRecordForm
    inlines = (GroupInline,)
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
        return sorted(list(set(list_of_users + [("all", "all"), ])), key=lambda tp: tp[1])

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


@admin.register(RequestJob)
class RequestJobAdmin(admin.ModelAdmin):
    class Media:
        js = ('js/multiselect.js',)
        css = {
            'all': ('css/db_copy.css',)
        }

    actions = ['resubmit_jobs', ]

    def resubmit_jobs(self, request, queryset):
        for query in queryset:
            newJob = RequestJob.objects.get(pk=query.pk)
            newJob.pk = None
            newJob.request_date = None
            newJob.start_date = None
            newJob.end_date = None
            newJob.status = None
            newJob.save()
            message = 'Job {} resubmitted [new job_id {}]'.format(query.pk, newJob.pk)
            messages.add_message(request, messages.SUCCESS, message, extra_tags='', fail_silently=False)

    resubmit_jobs.short_description = 'Resubmit Jobs'

    form = SubmitForm

    list_display = ('job_id', 'src_host', 'src_incl_db', 'src_skip_db', 'tgt_host', 'tgt_db_name', 'user',
                    'start_date', 'end_date', 'request_date', 'overall_status')
    search_fields = ('job_id', 'src_host', 'src_incl_db', 'src_skip_db', 'tgt_host', 'tgt_db_name', 'user',
                     'start_date', 'end_date', 'request_date')
    list_filter = ('tgt_host', 'src_host', UserFilter, OverallStatusFilter)
    ordering = ('-request_date', '-start_date')

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        # Allow delete only for superusers and obj owners
        return request.user.is_superuser or (obj is not None and request.user.username == obj.user)

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.user = request.user
        return form

    def change_view(self, request, object_id, form_url='', extra_context=None):
        context = extra_context or {}
        search_query = request.GET.get('search_box')
        if search_query:
            transfers_logs = self.get_object(request, object_id).transfer_logs.filter(
                Q(table_name__contains=search_query) | Q(table_schema__contains=search_query) | Q(
                    tgt_host__contains=search_query) | Q(renamed_table_schema__contains=search_query))
        else:
            transfers_logs = self.get_object(request, object_id).transfer_logs
        paginator = Paginator(transfers_logs.order_by(F('end_date').asc(nulls_first=True), F('auto_id')), 30)
        page_number = request.GET.get('page', 1)
        page = paginator.page(page_number)
        context['transfer_logs'] = page
        if transfers_logs.filter(end_date__isnull=True):
            context["running_copy"] = transfers_logs.filter(end_date__isnull=True).order_by(
                F('end_date').desc(nulls_first=True)).earliest('auto_id')
        return super().change_view(request, object_id, form_url, context)

    def _get_deletable_objects(self, queryset):
        return queryset.exclude(Q(status='Creating Requests') | Q(status='Processing Requests'))

    def get_deleted_objects(self, queryset, request):
        deletable_queryset = self._get_deletable_objects(queryset)
        return super().get_deleted_objects(deletable_queryset, request)

    def delete_queryset(self, request, queryset):
        deletable_queryset = self._get_deletable_objects(queryset)
        deleted_count, _rows_count = deletable_queryset.delete()
        message = "Successfully deleted %(count)d %(items)s." % {
                'count': deleted_count, 'items': model_ngettext(self.opts, deleted_count)
        }
        messages.add_message(request, messages.SUCCESS, message, extra_tags='', fail_silently=False)

    def message_user(self, *args, **kwargs):
        pass

    def log_deletion(self, request, obj, obj_display):
        if obj.status != 'Creating Requests' and obj.status != 'Processing Requests':
            super().log_deletion(request, obj, obj_display)

    def overall_status(self, obj):
        return format_html(
            '<div class="overall_status {}">{}</div>',
            obj.overall_status,
            obj.overall_status,
        )
