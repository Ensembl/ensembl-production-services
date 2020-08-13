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

from django.shortcuts import render
from django.views.generic import TemplateView
from jira import JIRA
from ensembl_production.models import Credentials


class IntentionsView(TemplateView):
    template_name = 'intentions.html'

    def get_context_data(self, **kwargs):
        jira_issues = get_jira_issues()
        context = super().get_context_data(**kwargs)
        context['intentions'] = jira_issues
        return context

class IntentionView2(IntentionsView):

    def get_context_data(self, **kwargs):
        jira_issues = get_jira_issues(issuetype='Epic')
        print(jira_issues)
        context = super().get_context_data(**kwargs)
        context['intentions'] = jira_issues
        return context


def intentions_export(request):
    jira_issues = get_jira_issues(request)
    return render(
        request,
        'intentions_export.html',
        {'intentions': jira_issues},
        'application/force-download'
    )


def get_jira_issues(request=None, **kwargs):
    jira_credentials = Credentials.objects.get(cred_name="Jira")
    jira = JIRA(server=jira_credentials.cred_url,
                basic_auth=(jira_credentials.user, jira_credentials.credentials))

    name_map = {field['name']: field['id'] for field in jira.fields()}
    issuetype = kwargs.get('issuetype', 'Bug')
    jira_filter = \
        'project = ENSINT AND ' + \
        'issuetype = ' + issuetype + \
        ' ORDER BY Rank DESC'
    #+ ' AND ' + \
    #'Website in (Archives, Blog, GRCh37, "Live site", Mirrors, Mobile) ' + \

    jira_issues = jira.search_issues(jira_filter, expand='renderedFields')

    separator = ', '
    for jira_issue in jira_issues:
        setattr(jira_issue, 'versions_list', separator.join(v.name for v in jira_issue.fields.versions))
        setattr(jira_issue, 'workaround', getattr(jira_issue.renderedFields, name_map['Work Around']))
        websites = getattr(jira_issue.fields, name_map['Website']) or []
        setattr(jira_issue, 'affected_sites', separator.join(w.value for w in websites))

    if request is not None:
        if request.method == 'POST' and 'intentions_filter' in request.POST:
            jira_issues = [x for x in jira_issues if matches_filter(x, request.POST['intentions_filter'])]

    return jira_issues


def matches_filter(jira_issue, intentions_filter):
    fields_string = " ".join(filter(None, [
        jira_issue.key,
        jira_issue.fields.summary,
        jira_issue.fields.description,
        jira_issue.affected_sites,
        jira_issue.versions_list,
        jira_issue.workaround
    ]))
    escaped_filter = re.escape(intentions_filter)
    return re.search(escaped_filter, fields_string)
