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

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ensembl_production_db.api.serializers import WebDataSerializer
from ensembl_production_db.models import *

User = get_user_model()


class AnalysisTest(APITestCase):
    """ Test module for AnalysisDescription model """
    multi_db = True
    using_db = 'production'
    fixtures = ['ensembl_production_api']

    # Test Analysis description endpoints
    def testAnalysisDescriptionPost(self):
        # Check get list
        response = self.client.get(reverse('analysisdescription-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 45)
        # Test Create a new one
        payload = {
            'logic_name': 'test',
            'description': 'test analysis',
            'display_label': 'test',
            'db_version': 1,
            'displayable': 1
        }
        response = self.client.post(reverse('analysisdescription-list'),
                                    data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # test first get
        first_analysis = AnalysisDescription.objects.get(logic_name='test')
        self.assertIsNotNone(first_analysis)
        self.assertIsNone(first_analysis.web_data)
        # Test create with WebData
        webdata_data_payload = {
            'default': {
                'contigviewbottom': 'normal'
            },
            'dna_align_feature': {
                'do_not_display': '1'
            },
            'type': 'cdna'
        }
        webdata_payload = {
            'description': 'test',
            'data': webdata_data_payload
        }
        analysis_payload = {
            'logic_name': 'webdata',
            'description': 'testwebdata analysis',
            'display_label': 'testwebdata',
            'db_version': 1,
            'displayable': 1,
            'web_data': webdata_payload
        }
        response = self.client.post(reverse('analysisdescription-list'),
                                    data=json.dumps(analysis_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        analysis = AnalysisDescription.objects.get(logic_name='webdata')
        self.assertIsNotNone(analysis)
        web_data = analysis.web_data
        self.assertEqual(web_data.description, 'test')
        self.assertDictEqual(web_data.data, webdata_data_payload)

        self.assertTrue('dna_align_feature' in web_data.data)
        self.assertTrue('type' in web_data.data and web_data.data['type'] == 'cdna')
        web_data_id = web_data.web_data_id
        # Test post wth webdata, reusing and updating existing webdata
        analysis_payload = {
            'logic_name': 'webdata2',
            'description': 'testwebdata2 analysis',
            'display_label': 'testwebdata2',
            'db_version': 1,
            'displayable': 1,
            'web_data': {
                'description': 'updated description',
                'data': webdata_data_payload
            }
        }
        response = self.client.post(reverse('analysisdescription-list'),
                                    data=json.dumps(analysis_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        analysis = AnalysisDescription.objects.filter(logic_name='webdata2').first()
        self.assertIsNotNone(analysis)
        web_data = analysis.web_data
        self.assertEqual(web_data.description, 'updated description')
        self.assertEqual(web_data.web_data_id, web_data_id)
        self.assertDictEqual(web_data.data, webdata_data_payload)
        # Test get wth webdata
        response = self.client.get(reverse('analysisdescription-detail', kwargs={'logic_name': 'webdata'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('description' in response.data)
        [self.assertTrue(key in response.data['web_data']) for key in webdata_payload.keys()]

    def testAnalysisDescriptionPut(self):
        # Test bad post
        analysis_payload = {
            'logic_name': '',
            'description': 'test analysis',
            'display_label': 'test',
            'db_version': 1,
            'displayable': 1
        }
        response = self.client.post(reverse('analysisdescription-list'),
                                    data=json.dumps(analysis_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('logic_name', response.data)
        # Test get wrong logic_name
        response = self.client.get(reverse('analysisdescription-detail', kwargs={'logic_name': 'unknown'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Test put
        response = self.client.get(reverse('analysisdescription-detail', kwargs={'logic_name': 'ab_initio_repeatmask'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['display_label'], 'Repeats (from Recon)')
        first_analysis = AnalysisDescription.objects.get(logic_name='ab_initio_repeatmask')
        update_analysis_payload = {
            'logic_name': 'ab_initio_repeatmask',
            'description': 'analysis updated description',
            'display_label': 'new display label',
            'db_version': 1,
            'displayable': 1
        }
        response = self.client.put(reverse('analysisdescription-detail',
                                           kwargs={'logic_name': 'ab_initio_repeatmask'}),
                                   data=json.dumps(update_analysis_payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_analysis = AnalysisDescription.objects.get(logic_name='ab_initio_repeatmask')
        self.assertEqual(updated_analysis.analysis_description_id, first_analysis.analysis_description_id)
        self.assertGreater(updated_analysis.modified_at, first_analysis.modified_at)
        self.assertEqual(updated_analysis.display_label, 'new display label')
        self.assertEqual(updated_analysis.description, 'analysis updated description')
        # Test bad put
        response = self.client.put(reverse('analysisdescription-detail', kwargs={'logic_name': 'dontexist'}),
                                   {
                                       'logic_name': 'newtest',
                                       'description': 'newtest2 analysis',
                                       'display_label': 'newtest2',
                                       'db_version': 1,
                                       'displayable': 1
                                   })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Test put changing webdata
        analysis_payload = {
            'logic_name': 'ab_initio_repeatmask',
            'description': 'Updated test analysis',
            'display_label': 'testwebdata2',
            'db_version': 1, 'displayable': 1,
            'web_data': {
                'description': 'Updated we Data',
                'data': {
                    'default': {
                        'contigviewbottom': 'notnormal'
                    },
                    'dna_align_feature': {
                        'do_not_display': '1'
                    },
                    'type': 'cdna'
                }
            }
        }

        response = self.client.put(reverse('analysisdescription-detail',
                                           kwargs={'logic_name': 'ab_initio_repeatmask'}),
                                   data=json.dumps(analysis_payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_analysis = AnalysisDescription.objects.get(logic_name='ab_initio_repeatmask')
        self.assertEqual(updated_analysis.web_data.description, 'Updated we Data')

    def testAnalysisDescriptionPatch(self):
        # Test bad put changing webdata
        valid_payload = {
            'logic_name': 'testwebtestdata2',
            'description': 'testwebdata2 analysis',
            'display_label': 'testwebdata2',
            'db_version': 1,
            'displayable': 1,
            'web_data': {
                'description': 'test2',
                'data': {
                    'default': {
                        'contigviewbottom': 'notnormal'
                    },
                    'dna_align_feature': {
                        'do_not_display': '1'
                    },
                    'type': 'cdna'
                }
            }
        }
        response = self.client.patch(reverse('analysisdescription-detail',
                                             kwargs={'logic_name': 'dontexistwebdata'}),
                                     data=json.dumps(valid_payload),
                                     content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Test patch
        analysis_payload = {
            'logic_name': 'test3',
            'description': 'test2 analysis updated',
            'display_label': 'test2',
            'db_version': 1,
            'displayable': 1
        }
        response = self.client.patch(reverse('analysisdescription-detail',
                                             kwargs={'logic_name': 'assembly_patch_ensembl'}),
                                     data=json.dumps(analysis_payload),
                                     content_type='application/json'
                                     )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test get
        response = self.client.get(reverse('analysisdescription-detail',
                                           kwargs={'logic_name': 'test3'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test bad patch
        wrong_analysis_payload = {
            'logic_name': 'newtest',
            'description': 'newtest2 analysis',
            'display_label': 'newtest2',
            'db_version': 1,
            'displayable': 1
        }

        response = self.client.patch(reverse('analysisdescription-detail',
                                             kwargs={'logic_name': 'dontexist2'}),
                                     data=json.dumps(wrong_analysis_payload),
                                     content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Test patch wth webdata
        webdata_payload = {
            'description': 'test',
            'data': {
                'default': {'contigviewbottom': 'normal'},
                'dna_align_feature': {'do_not_display': '1'},
                'type': 'core'}
        }
        valid_payload = {
            'logic_name': 'bacends',
            'description': 'testwebdata analysis',
            'display_label': 'testwebdata',
            'db_version': 1,
            'displayable': 1,
            'web_data': webdata_payload
        }
        response = self.client.patch(reverse('analysisdescription-detail',
                                             kwargs={'logic_name': 'bacends'}),
                                     data=json.dumps(valid_payload),
                                     content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test delete
        response = self.client.delete(reverse('analysisdescription-detail', kwargs={'logic_name': 'bgi_genewise_geneset'}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Test post wth webdata, reusing existing webdata for delete
        valid_payload = {
            'logic_name': 'testwebtestdata3',
            'description': 'testwebdata3 analysis',
            'display_label': 'testwebdata3',
            'db_version': 1,
            'displayable': 1,
            'web_data': webdata_payload
        }
        response = self.client.post(reverse('analysisdescription-list'),
                                    data=json.dumps(valid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_elem = AnalysisDescription.objects.get(logic_name='testwebtestdata3')
        self.assertIsNotNone(new_elem.web_data.data)
        self.assertTrue('default' in new_elem.web_data.data)
        self.assertEqual(new_elem.web_data.data['default']['contigviewbottom'], 'normal')
        self.assertIsNotNone(WebData.objects.get(description='test'))
        # Test get after deleted webdata
        response = self.client.get(reverse('analysisdescription-detail', kwargs={'logic_name': 'testwebtestdata3'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test bad delete
        response = self.client.delete(reverse('analysisdescription-detail', kwargs={'logic_name': 'cantdeleteit'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def testAnalysisDescriptionUserName(self):
        valid_payload = {'logic_name': 'testwebtestdata4',
                         'description': 'testwebdata4 analysis',
                         'display_label': 'testwebdata4',
                         'db_version': 1,
                         'displayable': 1, "user": "testuser",
                         'web_data': {
                             'description': 'test',
                             'data': {
                                 'default': {
                                     'contigviewbottom': 'normal'
                                 },
                                 'dna_align_feature': {
                                     'do_not_display': '1'
                                 },
                                 'type': 'core'}
                         }}
        response = self.client.post(reverse('analysisdescription-list'), data=json.dumps(valid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='testuser')
        new_elem = AnalysisDescription.objects.get(logic_name='testwebtestdata4')
        self.assertEqual(new_elem.created_by.username, user.username)

        valid_payload.update({'user': 'unknownuser', 'logic_name': 'failed_one'})
        response = self.client.post(reverse('analysisdescription-list'), data=json.dumps(valid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        valid_payload = {'logic_name': 'testwebtestdata5',
                         'description': 'testwebdata5 analysis',
                         'display_label': 'testwebdata5',
                         'db_version': 1,
                         'displayable': 1,
                         'web_data': {
                             'description': 'test',
                             'data': {
                                 'default': {
                                     'contigviewbottom': 'normal'
                                 },
                                 'dna_align_feature': {
                                     'do_not_display': '1'
                                 },
                                 'type': 'core'}
                         }
                         }
        response = self.client.post(reverse('analysisdescription-list'), data=json.dumps(valid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_elem = AnalysisDescription.objects.get(logic_name='testwebtestdata5')
        self.assertIsNone(new_elem.created_by)
        self.assertIsNotNone(new_elem.web_data.data)
        self.assertTrue(json.dumps(new_elem.web_data.data))
        # test update with username
        valid_payload = {'logic_name': 'testwebtestdata5',
                         'description': 'testwebdata5 analysis updated',
                         'display_label': 'testwebdata5',
                         'db_version': 1,
                         'displayable': 1,
                         'user': "testuserupdate"
                         }
        response = self.client.patch(reverse('analysisdescription-detail', kwargs={'logic_name': 'testwebtestdata5'}),
                                     data=json.dumps(valid_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_elem = AnalysisDescription.objects.get(logic_name='testwebtestdata5')
        self.assertIsNotNone(new_elem.modified_by)
        self.assertIsNotNone(new_elem.web_data.data)
        self.assertTrue('dna_align_feature' in new_elem.web_data.data)
        self.assertEqual(new_elem.web_data.data['dna_align_feature']['do_not_display'], '1')
        self.assertEqual(new_elem.modified_by.username, 'testuserupdate')
        # test unknown user
        valid_payload = {'logic_name': 'testwebtestdata5', 'description': 'testwebdata5 analysis updated wrong user',
                         'display_label': 'testwebdata5', 'db_version': 1, 'displayable': 1, 'user': "unknownuser"}
        response = self.client.patch(reverse('analysisdescription-detail', kwargs={'logic_name': 'testwebtestdata5'}),
                                     data=json.dumps(valid_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        valid_payload = {'logic_name': 'testwebtestdata5',
                         'description': 'testwebdata5 analysis',
                         'display_label': 'testwebdata5',
                         'db_version': 1,
                         'displayable': 1,
                         'web_data': {
                             'description': 'test',
                             'data': {
                                 'default': 'normalupdated'
                             }
                         }}
        response = self.client.put(reverse('analysisdescription-detail', kwargs={'logic_name': 'testwebtestdata5'}),
                                   data=json.dumps(valid_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        analysis = AnalysisDescription.objects.get(logic_name='testwebtestdata5')
        self.assertEqual(analysis.web_data.data, json.loads('{"default": "normalupdated"}'))
        self.assertEqual(WebData.objects.filter(data__contains="normalupdated").count(), 1)

    def testWebDataCreateUpdate(self):
        valid_payload = {
            "user": "testuser",
            "web_data": {
                "data": {
                    "zmenu": "RNASeq_bam",
                    "label_key": "RNASeq [biotype]",
                    "colour_key": "bam",
                    "type": "rnaseq",
                    "matrix": {
                        "group_order": "1",
                        "column": "BAM files",
                        "menu": "rnaseq",
                        "group": "ENA",
                        "row": "cruk brain"
                    }
                }
            },
            "logic_name": "sus_scrofa_cruk_brain_rnaseq_bam",
            "description": "BWA alignments of cruk brain RNA-seq data. This BAM file can be downloaded from the <a href=\"ftp://ftp.ensembl.org/pub/data_files/\">Ensembl FTP site</a>",
            "display_label": "cruk brain RNA-seq BWA alignments"
        }
        response = self.client.post(reverse('analysisdescription-list'),
                                    data=json.dumps(valid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_elem = AnalysisDescription.objects.get(logic_name='sus_scrofa_cruk_brain_rnaseq_bam')
        self.assertIsNone(new_elem.modified_by)
        self.assertEqual(new_elem.created_by.username, 'testuser')
        wdata_ser = WebDataSerializer(data=valid_payload["web_data"])
        if wdata_ser.is_valid():
            web_data = valid_payload["web_data"]["data"]
            self.assertIsNotNone(web_data)
            self.assertEqual(json.dumps(wdata_ser.validated_data['data'], sort_keys=True),
                             json.dumps(web_data, sort_keys=True))

        another_valid_payload = {
            "user": "testuser",
            "web_data": {
                "data": {
                    "zmenu": "RNASeq_bam",
                    "label_key": "RNASeq [biotype]",
                    "colour_key": "bam",
                    "type": "rnaseq",
                    "matrix": {
                        "group_order": "1",
                        "column": "BAM files",
                        "menu": "rnaseq",
                        "group": "ENA",
                        "row": "cruk brain"
                    }
                }
            },
            "logic_name": "other_logic_name",
            "description": "BWA alignments of cruk brain RNA-seq data. T",
            "display_label": "cruk brain RNA-seq BWA alignments"
        }
        response = self.client.post(reverse('analysisdescription-list'),
                                    data=json.dumps(another_valid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_elem_same_data = AnalysisDescription.objects.get(logic_name='other_logic_name')
        self.assertEqual(new_elem.web_data_id, new_elem_same_data.web_data_id)

    # Test attrib Type endpoint
    def testAttribType(self):
        # Check get all
        response = self.client.get(reverse('attribtypes-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test post
        response = self.client.post(reverse('attribtypes-list'),
                                    {'code': 'test', 'name': 'test attribtypes', 'description': 'test'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Test duplicated code post
        response = self.client.post(reverse('attribtypes-list'),
                                    {'code': 'test', 'name': 'test attribtypes', 'description': 'test'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Test bad post
        response = self.client.post(reverse('attribtypes-list'),
                                    {'code': '', 'name': 'test attribtypes', 'description': 'test'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Test get
        response = self.client.get(reverse('attribtypes-detail', kwargs={'code': 'test'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test bad get
        response = self.client.get(reverse('attribtypes-detail', kwargs={'code': 'cantgetit'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Test put
        response = self.client.put(reverse('attribtypes-detail', kwargs={'code': 'test'}),
                                   {'code': 'test2', 'name': 'test2 attribtypes', 'description': 'test2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test bad put
        response = self.client.put(reverse('attribtypes-detail', kwargs={'code': 'dontexist'}),
                                   {'code': 'newtest', 'description': 'newtest2 analysis', 'name': 'newtest2'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Test patch
        response = self.client.patch(reverse('attribtypes-detail', kwargs={'code': 'test2'}),
                                     {'code': 'test3', 'description': 'test2 analysis updated', 'name': 'test2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test bad patch
        response = self.client.patch(reverse('attribtypes-detail', kwargs={'code': 'dontexist2'}),
                                     {'code': 'newtest', 'description': 'newtest2 analysis', 'name': 'newtest2'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Test delete
        response = self.client.delete(reverse('attribtypes-detail', kwargs={'code': 'test3'}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Test bad delete
        response = self.client.delete(reverse('attribtypes-detail', kwargs={'code': 'cantdeleteit'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def testAttribTypeUserName(self):
        # create user known
        response = self.client.post(reverse('attribtypes-list'),
                                    {'code': 'test', 'name': 'test attribtypes', 'description': 'test',
                                     'user': 'testuser'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_elem = MasterAttribType.objects.get(code='test')
        user = User.objects.get(username='testuser')
        self.assertEqual(new_elem.created_by.username, user.username)
        # create user un-known
        response = self.client.post(reverse('attribtypes-list'),
                                    {'code': 'test2', 'name': 'test attribtypes', 'description': 'test',
                                     'user': 'unknown'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # update user known
        response = self.client.put(reverse('attribtypes-detail', kwargs={'code': 'test'}),
                                   {'code': 'test', 'name': 'test2 attribtypes', 'description': 'test2',
                                    'user': 'testuser'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_elem = MasterAttribType.objects.get(code='test')
        self.assertEqual(new_elem.modified_by.username, user.username)
        # update user un-known
        response = self.client.put(reverse('attribtypes-detail', kwargs={'code': 'test'}),
                                   {'code': 'test', 'name': 'test2 attribtypes', 'description': 'test2',
                                    'user': 'unknown'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test biotype endpoint
    def testBiotype(self):
        # Test post object type 1
        response = self.client.post(reverse('type-list', kwargs={'biotype_name': 'test'}),
                                    {'name': 'test', 'description': 'test biotype gene', 'object_type': 'gene',
                                     'db_type': 'core', 'is_dumped': 1})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Test post object type 2
        response = self.client.post(reverse('type-list', kwargs={'biotype_name': 'test'}),
                                    {'name': 'test', 'description': 'test biotype transcript',
                                     'object_type': 'transcript', 'db_type': 'core', 'is_dumped': 1})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Test bad post
        response = self.client.post(reverse('type-list', kwargs={'biotype_name': 'badtest'}),
                                    {'name': '', 'description': 'test biotype', 'display_label': 'test',
                                     'object_type': 'gene', 'db_type': 'core', 'is_dumped': 1})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Test get
        response = self.client.get(reverse('type-list', kwargs={'biotype_name': 'test'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test bad get
        response = self.client.get(reverse('type-list', kwargs={'biotype_name': 'cantgetit'}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Test get wth types
        response = self.client.get(reverse('type-detail', kwargs={'biotype_name': 'test', 'type': 'gene'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test bad get wth types
        response = self.client.get(reverse('type-detail', kwargs={'biotype_name': 'cantgetit', 'type': 'gene'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Test put
        response = self.client.put(reverse('type-detail', kwargs={'biotype_name': 'test', 'type': 'gene'}),
                                   {'name': 'test2', 'description': 'test2 biotype updated', 'object_type': 'gene',
                                    'db_type': 'core', 'is_dumped': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test bad put
        response = self.client.put(reverse('type-detail', kwargs={'biotype_name': 'dontexist', 'type': 'gene'}),
                                   {'name': 'newtest', 'description': 'newtest2 biotype', 'object_type': 'gene',
                                    'db_type': 'core', 'is_dumped': 1})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Test patch
        response = self.client.patch(reverse('type-detail', kwargs={'biotype_name': 'test2', 'type': 'gene'}),
                                     {'name': 'test3', 'description': 'test2 biotype updated', 'object_type': 'gene',
                                      'db_type': 'core', 'is_dumped': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test bad patch
        response = self.client.patch(reverse('type-detail', kwargs={'biotype_name': 'dontexist2', 'type': 'gene'}),
                                     {'name': 'newtest', 'description': 'newtest2 biotype', 'object_type': 'gene',
                                      'db_type': 'core', 'is_dumped': 1})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Test delete
        response = self.client.delete(reverse('type-detail', kwargs={'biotype_name': 'test3', 'type': 'gene'}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Test bad delete
        response = self.client.delete(reverse('type-detail', kwargs={'biotype_name': 'cantdeleteit', 'type': 'gene'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def testBiotypeUserName(self):
        # Test post object type 1
        response = self.client.post(reverse('type-list', kwargs={'biotype_name': 'test'}),
                                    {'name': 'test', 'description': 'test biotype gene', 'object_type': 'gene',
                                     'db_type': 'core', 'is_dumped': 1, 'user': 'testuser'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_elem = MasterBiotype.objects.get(name='test')
        user = User.objects.get(username='testuser')
        self.assertEqual(new_elem.created_by.username, user.username)
        response = self.client.put(reverse('type-detail', kwargs={'biotype_name': 'test', 'type': 'gene'}),
                                   {'name': 'test update', 'description': 'test2 biotype updated',
                                    'object_type': 'gene',
                                    'db_type': 'core', 'is_dumped': 1, 'user': 'testuser'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_elem = MasterBiotype.objects.get(name='test update')
        self.assertEqual(new_elem.modified_by.username, user.username)
        response = self.client.put(reverse('type-detail', kwargs={'biotype_name': 'test update', 'type': 'gene'}),
                                   {'name': 'test update', 'description': 'test2 biotype updated',
                                    'object_type': 'gene', 'db_type': 'core', 'is_dumped': 1, 'user': 'unknown'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(reverse('type-list', kwargs={'biotype_name': 'test'}),
                                    {'name': 'test another', 'description': 'test biotype gene', 'object_type': 'gene',
                                     'db_type': 'core', 'is_dumped': 1, 'user': 'unknown'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test attrib endpoint
    def testAttrib(self):
        # Check get all
        response = self.client.get(reverse('attrib-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test post wth attrib_type
        valid_payload = {'value': 'test', 'is_current': '1',
                         'attrib_type': {'code': 'test', 'name': 'test', 'description': 'test'}}
        response = self.client.post(reverse('attrib-list'), data=json.dumps(valid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        attrib_type = MasterAttrib.objects.filter(value='test').first().attrib_type
        self.assertIsNotNone(MasterAttrib.objects.filter(value='test').first().attrib_type)
        # Test post wth attrib_type, reusing existing attrib_type
        valid_payload = {'value': 'test2', 'is_current': '1',
                         'attrib_type': {'code': 'test', 'name': 'test', 'description': 'test'}}
        response = self.client.post(reverse('attrib-list'), data=json.dumps(valid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(MasterAttrib.objects.filter(value='test2').first().attrib_type.pk == attrib_type.pk)
        # Test bad post
        valid_payload = {'value': '', 'is_current': '1',
                         'attrib_type': {'code': 'test', 'name': 'test', 'description': 'test'}}
        response = self.client.post(reverse('attrib-list'), data=json.dumps(valid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def testAttribUserName(self):
        valid_payload = {'value': 'test', 'is_current': '1', 'user': 'testuser',
                         'attrib_type': {'code': 'test', 'name': 'test', 'description': 'test'}}
        response = self.client.post(reverse('attrib-list'), data=json.dumps(valid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_elem = MasterAttrib.objects.get(attrib_type__code='test')
        user = User.objects.get(username='testuser')
        self.assertEqual(new_elem.created_by.username, user.username)
        self.assertEqual(new_elem.attrib_type.created_by.username, user.username)
