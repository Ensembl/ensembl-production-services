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

# fake models to allow standard admin integration.
import re

from django.db import models
from jira import JIRA

from ensembl_production.models import Credentials


def matches_filter(jira_issue, intentions_filter):
    fields_string = " ".join(filter(None, [
        getattr(jira_issue, field_name) for field_name in jira_issue.filter_on
    ]))
    escaped_filter = re.escape(intentions_filter)
    return re.search(escaped_filter, fields_string)


class JiraManager(models.Manager):
    _field_list = ()

    def all(self):
        jira_credentials = Credentials.objects.get(cred_name="Jira")
        jira = JIRA(server=jira_credentials.cred_url,
                    basic_auth=(jira_credentials.user, jira_credentials.credentials))
        name_map = {field['name']: field['id'] for field in jira.fields()}
        jira_issues = jira.search_issues(self.model.jira_filter, expand='renderedFields')
        return [self.model(issue=jira_issue, name_map=name_map) for jira_issue in jira_issues]

    def filter(self, filter_terms):
        issues = self.all()
        if filter_terms is not None:
            issues = [x for x in issues if matches_filter(x, filter_terms)]
        return issues


class JiraFakeModel(models.Model):
    ''' Readonly fake models to allow easy JIRA ticket listing integration in Django backend. '''

    class Meta:
        db_table = "jira"
        app_label = 'ensembl_intentions'

    export_template_name = "intentions_export.html"
    export_file_name = "export.txt"
    objects = JiraManager()

    def __init__(self, issue, name_map):
        # short cut attributes to jira_issues ones
        super().__init__()
        self.permalink = issue.permalink
        self.key = issue.key
        self.summary = issue.fields.summary
        self.description = issue.fields.description
        self.contact = issue.fields.reporter.emailAddress


class Intention(JiraFakeModel):
    jira_filter = 'project = ENSINT AND issuetype = Epic AND fixVersion in unreleasedVersions() ' \
                  'ORDER BY fixVersion DESC, goal ASC, Rank DESC'
    template = 'intention.html'
    filter_on = (
        'key',
        'summary',
        'description',
        'target_version',
        'declaration_type',
        'declaring_team'
    )

    class Meta:
        proxy = True
        verbose_name = "Release Intention"

    def __init__(self, issue, name_map):
        super().__init__(issue, name_map)
        self.declaring_team = getattr(issue.fields, name_map['Declaring Team']).value
        self.declaration_type = getattr(issue.fields, name_map['Goal']).value
        self.target_version = issue.fields.fixVersions[0].name if issue.fields.fixVersions else 'N/A'


class KnownBug(JiraFakeModel):
    jira_filter = 'project = ENSINT AND issuetype = Bug AND Website in ' \
                  '(Archives, Blog, GRCh37, "Live site", Mirrors, Mobile) ' \
                  ' and status not in (Closed, "Under review") ORDER BY Rank DESC'
    template = 'knownbug.html'
    filter_on = (
        'key',
        'summary',
        'description',
        'affected_sites',
        'versions_list',
        'workaround'
    )

    class Meta:
        proxy = True
        verbose_name = "Known bug"

    def __init__(self, issue, name_map):
        super().__init__(issue, name_map)
        self.versions_list = ', '.join(v.name for v in issue.fields.versions)
        self.workaround = getattr(issue.renderedFields, name_map['Work Around'])
        websites = getattr(issue.fields, name_map['Website']) or []
        self.affected_sites = ', '.join(w.value for w in websites)


class RRBug(JiraFakeModel):
    class Meta:
        proxy = True
        verbose_name = "Rapid Release Bug"

    export_template_name = "rapid_export.html"
    export_file_name = "known_bugs.inc"
    jira_filter = 'project = "Ensembl Rapid Release" ' \
                  'AND issuetype = Bug AND status not in (Closed, Done, "In Review")' \
                  'AND resolution is EMPTY ORDER BY updatedDate DESC'
    template = 'rapid.html'
    filter_on = (
        'key',
        'summary',
        'description',
    )
