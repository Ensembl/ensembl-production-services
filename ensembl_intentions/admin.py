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

from ensembl_production.admin import ProductionUserAdminMixin
from .views import IntentionsView, IntentionView2, get_jira_issues
from .models import Intention, KnownBug

class JiraAdminMixin(admin.ModelAdmin):
    readonly_fields = []
    _issuetype = None
    change_list_template = 'jira_issue_list.html'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        extra_context = {'intentions': self.model._default_manager.all()}
        return super().changelist_view(request, extra_context)


@admin.register(Intention)
class IntentionAdmin(JiraAdminMixin):
    pass

@admin.register(KnownBug)
class KnownBugAdmin(JiraAdminMixin):
    pass