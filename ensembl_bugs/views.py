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
from django.shortcuts import render
from django.views.generic import TemplateView
from jira import JIRA
import re

from .models import Credentials


class KnownBugsView(TemplateView):
    template_name = 'known_bugs.html'

    def get_context_data(self, **kwargs):
        jira_issues = get_jira_issues()
        context = super().get_context_data(**kwargs)
        context['known_bugs'] = jira_issues
        return context


def known_bugs_export(request):
    jira_issues = get_jira_issues(request)
    return render(
        request,
        'known_bugs_export.html',
        {'known_bugs': jira_issues},
        'application/force-download'
    )


def get_jira_issues(request=None):
    jira_credentials = Credentials.objects.get(cred_name="Jira")
    jira = JIRA(server=jira_credentials.cred_url,
                basic_auth=(jira_credentials.user, jira_credentials.credentials))

    name_map = {field['name']: field['id'] for field in jira.fields()}

    jira_filter =\
        'project = ENSINT AND ' +\
        'issuetype = Bug AND ' + \
        'Website in (Archives, Blog, GRCh37, "Live site", Mirrors, Mobile) ' +\
        'ORDER BY Rank DESC'
    jira_issues = jira.search_issues(jira_filter, expand='renderedFields')

    separator = ', '
    for jira_issue in jira_issues:
        setattr(jira_issue, 'versions_list', separator.join(v.name for v in jira_issue.fields.versions))
        setattr(jira_issue, 'workaround', getattr(jira_issue.renderedFields, name_map['Work Around']))
        websites = getattr(jira_issue.fields, name_map['Website']) or []
        setattr(jira_issue, 'affected_sites', separator.join(w.value for w in websites))

    if request is not None:
        if request.method == 'POST' and 'known_bugs_filter' in request.POST:
            jira_issues = [x for x in jira_issues if matches_filter(x, request.POST['known_bugs_filter'])]

    return jira_issues


def matches_filter(jira_issue, known_bugs_filter):
    fields_string = " ".join(filter(None, [
        jira_issue.fields.summary,
        jira_issue.fields.description,
        jira_issue.affected_sites,
        jira_issue.versions_list,
        jira_issue.workaround
    ]))
    escaped_filter = re.escape(known_bugs_filter)
    return re.search(escaped_filter, fields_string)
