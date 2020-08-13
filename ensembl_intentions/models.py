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
from django.db import models
from jira import JIRA

from ensembl_intentions.views import matches_filter
from ensembl_production.models import Credentials


class JiraManager(models.Manager):
    _field_list = ()
    def all(self):
        jira_credentials = Credentials.objects.get(cred_name="Jira")
        jira = JIRA(server=jira_credentials.cred_url,
                    basic_auth=(jira_credentials.user, jira_credentials.credentials))

        name_map = {field['name']: field['id'] for field in jira.fields()}

        jira_issues = jira.search_issues(self.model.jira_filter, expand='renderedFields')
        return [self.model(issue=jira_issue, map=name_map) for jira_issue in jira_issues]

    def filter(self, *args, **kwargs):
        request = kwargs['request'] or None
        if request is not None:
            if request.method == 'POST' and 'intentions_filter' in request.POST:
                jira_issues = [x for x in self.all() if matches_filter(x, request.POST['intentions_filter'])]

        return jira_issues


class JiraFakeModel(models.Model):
    ''' Readonly fake models to allow easy JIRA ticket listing integration in Django backend. '''

    class Meta:
        db_table = "empty"
        verbose_name = "Known bug"


    objects = JiraManager()

    def __init__(self, issue, map):
        self.issue = issue
        self.map = map

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # DO NOTHING
        pass

    def cname(self):
        return self.__class__.__name__

class Intention(JiraFakeModel):
    jira_filter = 'project = ENSINT AND issuetype = Epic ORDER BY fixVersion DESC, Rank DESC'
    template = 'intention.html'

    class Meta:
        proxy = True


class KnownBug(JiraFakeModel):
    jira_filter = 'project = ENSINT AND issuetype = Bug AND Website in ' \
                  '(Archives, Blog, GRCh37, "Live site", Mirrors, Mobile) ' \
                  ' and status != Closed ORDER BY Rank DESC'
    template = 'knownbug.html'
    _field_list = ()
    class Meta:
        proxy = True

    def __init__(self, issue, map):
        super().__init__(issue, map)
        self.versions_list = ', '.join(v.name for v in issue.fields.versions)
        self.workaround = getattr(issue.renderedFields, map['Work Around'])
        websites = getattr(issue.fields, map['Website']) or []
        self.affected_sites = ', '.join(w.value for w in websites)
