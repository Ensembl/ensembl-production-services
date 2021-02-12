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
from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path

from .models import Intention, KnownBug, RRBug


class JiraAdmin(admin.ModelAdmin):
    readonly_fields = []
    change_list_template = 'jira_issue_list.html'
    export_template_name = "intentions_export.html"
    export_file_name = "export.txt"

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        my_urls = [
            path('export', self.admin_site.admin_view(self.export_view), name='%s_%s_export' % info)
        ]
        return my_urls + urls

    def has_add_permission(self, request):
        # No add
        return False

    def has_delete_permission(self, request, obj=None):
        # No delete
        return False

    def has_view_permission(self, request, obj=None):
        # View allowed to anyone from staff
        return request.user.is_staff

    def has_module_permission(self, request):
        # Allow module access to staff
        return request.user.is_staff

    def changelist_view(self, request, extra_context=None):
        extra_context = {
            'intentions': self.model._default_manager.all(),
            'export_verbose': self.model._meta.verbose_name,
            'export_view_name': 'admin:' + '_'.join([self.model._meta.app_label, self.model._meta.model_name, 'export'])
        }
        return super().changelist_view(request, extra_context)

    def export_view(self, request):
        context = dict(
            intentions=self.model._default_manager.filter(request.POST['intentions_filter'])
        )
        response = TemplateResponse(request, self.model.export_template_name, context, 'application/force-download')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(self.model.export_file_name)
        return response


@admin.register(Intention)
class IntentionAdmin(JiraAdmin):
    pass


@admin.register(KnownBug)
class KnownBugAdmin(JiraAdmin):
    pass


@admin.register(RRBug)
class RRBugAdmin(JiraAdmin):
    pass
