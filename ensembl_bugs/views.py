# -*- coding: utf-8 -*-
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
from django.views.generic import TemplateView
from .models import Credentials
from jira_project import JiraProject

from jira import JIRA


class KnownBugsView(TemplateView):
    template_name = "known_bugs.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        jira_credentials = Credentials.objects.get(cred_name="Jira")
        jira = JiraProject(credentials=(jira_credentials.user, jira_credentials.credentials), project_name='ENSINT',
                           version_name="Ensembl 99")
        known_bugs = jira.jira.search_issues("project = ENSINT AND issuetype = Bug ORDER BY Rank ASC")
        context['known_bugs'] = known_bugs
        return context
