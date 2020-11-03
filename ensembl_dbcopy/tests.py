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

import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

PRODUCTION_DB = settings.DATABASES.get('production', settings.DATABASES['default'])
User = get_user_model()


class RequestJobTest(APITestCase):
    """ Test module for RequestJob model """
    multi_db = True
    using_db = 'dbcopy'
    fixtures = ['ensembl_dbcopy']

    # Test requestjob endpoint
    def testRequestJob(self):
        # Check get all
        response = self.client.get(reverse('requestjob-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test post
        response = self.client.post(reverse('requestjob-list'),
                                    {'src_host': 'mysql-ens-sta-1', 'src_incl_db': 'homo_sapiens_core_99_38',
                                     'tgt_host': 'mysql-ens-general-dev-1', 'user': 'testuser'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Test user email
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict['email_list'], 'testuser@ebi.ac.uk')
        # Test bad post
        response = self.client.post(reverse('requestjob-list'),
                                    {'src_host': '', 'src_incl_db': 'homo_sapiens_core_99_38',
                                     'tgt_host': 'mysql-ens-general-dev-1'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Test get
        response = self.client.get(
            reverse('requestjob-detail', kwargs={'job_id': '8f084180-07ae-11ea-ace0-9801a79243a5'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test bad get
        response = self.client.get(
            reverse('requestjob-detail', kwargs={'job_id': 'd662656c-0a18-11ea-ab6c-9801a79243a5'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Test Transfer log
        response = self.client.get(
            reverse('requestjob-detail', kwargs={'job_id': 'ddbdc15a-07af-11ea-bdcd-9801a79243a5'}))
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(response_dict['transfer_log']), 2)
        # Test put
        response = self.client.put(
            reverse('requestjob-detail', kwargs={'job_id': '8f084180-07ae-11ea-ace0-9801a79243a5'}),
            {'src_host': 'mysql-ens-sta-1', 'src_incl_db': 'homo_sapiens_core_99_38',
             'tgt_host': 'mysql-ens-general-dev-2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test bad put
        response = self.client.put(
            reverse('requestjob-detail', kwargs={'job_id': 'd662656c-0a18-11ea-ab6c-9801a79243a5'}),
            {'src_host': 'mysql-ens-sta-1', 'src_incl_db': 'homo_sapiens_core_99_38',
             'tgt_host': 'mysql-ens-general-dev-2'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Test patch
        response = self.client.patch(
            reverse('requestjob-detail', kwargs={'job_id': '8f084180-07ae-11ea-ace0-9801a79243a5'}),
            {'src_incl_db': 'homo_sapiens_funcgen_99_38'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test bad patch
        response = self.client.patch(
            reverse('requestjob-detail', kwargs={'job_id': 'd662656c-0a18-11ea-ab6c-9801a79243a5'}),
            {'src_incl_db': 'homo_sapiens_funcgen_99_38'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Test delete
        response = self.client.delete(
            reverse('requestjob-detail', kwargs={'job_id': '8f084180-07ae-11ea-ace0-9801a79243a5'}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Test bad delete
        response = self.client.delete(
            reverse('requestjob-detail', kwargs={'job_id': '673f3b10-09e6-11ea-9206-9801a79243a5'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Test Source host endpoint
    def testSourceHost(self):
        # Test get
        response = self.client.get(reverse('src_host-detail', kwargs={'name': 'mysql-ens-sta-1'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test bad get
        response = self.client.get(reverse('src_host-detail', kwargs={'name': 'mysql-ens-compara-2'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Test getting 2 mysql-ens-sta-2 servers
        response = self.client.get(reverse('src_host-list'), {'name': 'mysql-ens-sta'})
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict['count'], 2)
        # Test getting mysql-ens-general-dev-1 server
        response = self.client.get(reverse('src_host-list'), {'name': 'mysql-ens-general'})
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict['count'], 2)

    # Test Target host endpoint
    def testTargetHost(self):
        # Test get
        response = self.client.get(reverse('tgt_host-detail', kwargs={'name': 'mysql-ens-sta-1'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test bad get
        response = self.client.get(reverse('tgt_host-detail', kwargs={'name': 'mysql-ens-compara-2'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Test getting 2 mysql-ens-sta servers with allowed user
        User.objects.get(username='testuser')
        self.client.login(username='testuser', password='testgroup123')
        response = self.client.get(reverse('tgt_host-list'), {'name': 'mysql-ens-sta'})
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict['count'], 2)
        # Test getting 2 mysql-ens-sta servers with non-allowed user
        User.objects.get(username='testuser2')
        self.client.login(username='testuser2', password='testgroup1234')
        response = self.client.get(reverse('tgt_host-list'), {'name': 'mysql-ens-sta'})
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict['count'], 1)
        # Test getting mysql-ens-general-dev-1 server
        response = self.client.get(reverse('tgt_host-list'), {'name': 'mysql-ens-general'})
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict['count'], 2)

    # Test DatabaseList endpoint
    def testDatabaseList(self):
        # Test getting test Production dbs

        response = self.client.get(reverse('databaselist'),
                                   {'host': PRODUCTION_DB.get('HOST', 'localhost'),
                                    'port': PRODUCTION_DB.get('PORT', 3306),
                                    'search': 'test_production_services'})
        response_list = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_list), 1)
        response = self.client.get(reverse('databaselist'),
                                   {'host': 'bad-host',
                                    'port': PRODUCTION_DB.get('PORT', 3306),
                                    'search': 'test_production_services'})
        response_list = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_list), 0)
        response = self.client.get(reverse('databaselist'),
                                   {'host': PRODUCTION_DB.get('HOST', 'localhost'),
                                    'port': PRODUCTION_DB.get('PORT', 3306),
                                    'search': 'no_result_search'})
        response_list = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_list), 0)
        response = self.client.get(reverse('databaselist'),
                                   {'host': PRODUCTION_DB.get('HOST', 'localhost'),
                                    'port': PRODUCTION_DB.get('PORT', 3306),
                                    'matches[]': ['test_production_services']})
        response_list = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_list), 1)
        response = self.client.get(reverse('databaselist'),
                                   {'host': PRODUCTION_DB.get('HOST', 'localhost'),
                                    'port': PRODUCTION_DB.get('PORT', 3306),
                                    'matches[]': ['no_match']})
        response_list = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_list), 0)
        response = self.client.get(reverse('databaselist'),
                                   {'host': PRODUCTION_DB.get('HOST', 'localhost'),
                                    'search': 'test_production_services'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test TableList endpoint
    def testTableList(self):
        # Test getting meta_key table for Production dbs
        response = self.client.get(reverse('tablelist'),
                                   {'host': PRODUCTION_DB.get('HOST', 'localhost'),
                                    'port': PRODUCTION_DB.get('PORT', 3306),
                                    'user': PRODUCTION_DB.get('USER', 'ensembl'),
                                    'database': PRODUCTION_DB.get('NAME', 'ensembl_tests'),
                                    'search': 'meta'})
        response_list = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_list), 1)
        response = self.client.get(reverse('tablelist'),
                                   {'host': PRODUCTION_DB.get('HOST', 'localhost'),
                                    'port': PRODUCTION_DB.get('PORT', 3306),
                                    'search': 'table_name'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.get(reverse('tablelist'),
                                   {'host': 'bad-host',
                                    'port': PRODUCTION_DB.get('PORT', 3306),
                                    'database': PRODUCTION_DB.get('NAME', 'ensembl_tests'),
                                    'search': 'meta'})
        response_list = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_list), 0)
        response = self.client.get(reverse('tablelist'),
                                   {'host': PRODUCTION_DB.get('HOST', 'localhost'),
                                    'port': PRODUCTION_DB.get('PORT', 3306),
                                    'database': 'not_a_database',
                                    'search': 'bad_table_name'})
        response_list = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_list), 0)

