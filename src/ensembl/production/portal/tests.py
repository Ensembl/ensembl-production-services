# See the NOTICE file distributed with this work for additional information
#   regarding copyright ownership.
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
from django.test import TestCase


class DBRoutingTest(TestCase):

    def testDBCopyRouting(self):
        from ensembl.production.dbcopy.models import Host, TransferLog, RequestJob
        hosts = Host.objects.all()
        self.assertEqual('dbcopy', hosts.db)
        tl = TransferLog.objects.all()
        self.assertEqual('dbcopy', tl.db)
        rj = RequestJob.objects.all()
        self.assertEqual('dbcopy', rj.db)

    def testWebHelpRouting(self):
        from ensembl.production.webhelp.models import HelpRecord, ViewRecord, LookupRecord, MovieRecord, FaqRecord
        h = HelpRecord.objects.all()
        self.assertEqual('website', h.db)
        vr = ViewRecord.objects.all()
        self.assertEqual('website', vr.db)
        lr = LookupRecord.objects.all()
        self.assertEqual('website', lr.db)
        mr = MovieRecord.objects.all()
        self.assertEqual('website', mr.db)
        fr = FaqRecord.objects.all()
        self.assertEqual('website', fr.db)

    def testMasterdbRouting(self):
        from ensembl.production.masterdb.models import MasterBiotype, MasterAttribType, MasterExternalDb
        m = MasterBiotype.objects.all()
        self.assertEqual('production', m.db)
        m = MasterExternalDb.objects.all()
        self.assertEqual('production', m.db)
        m = MasterAttribType.objects.all()
        self.assertEqual('production', m.db)

    def testPortalRouting(self):
        from ensembl.production.jira.models import JiraCredentials
        from ensembl.production.portal.models import ProductionApp
        m = JiraCredentials.objects.all()
        self.assertEqual('default', m.db)
        p = ProductionApp.objects.all()
        self.assertEqual('default', p.db)

class AppTests(TestCase):
    fixtures = ('groups', 'init')

    def testDeduplicateMenuEntry(self):
        from django.contrib.auth import get_user_model
        from django.contrib.auth.models import Group, User
        from ensembl.production.portal.models import AppView
        #user = get_user_model().objects.create(username="user1")
        user = User.objects.create(username="user1")
        groups = Group.objects.filter(name__in=['Production', 'Compara'])
        for group in groups:
            user.groups.add(group)

        user_apps = AppView.objects.user_apps(user).values_list('app_name')
        self.assertEqual(len(set(user_apps)), len(user_apps))


