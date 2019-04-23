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
from django.db import models

from ensembl_production.models import BaseTimestampedModel
from django_mysql.models import EnumField, SizedTextField

class WebSiteModel(BaseTimestampedModel):
    class Meta:
        app_label = 'website'
        abstract = True

"""
faq
view
lookup
movie
"""


class HelpRecord(WebSiteModel):
    _force_type = ''
    help_record_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=255)
    keyword = SizedTextField(size_class=1,blank=True, null=True)
    data = models.TextField()
    status = EnumField(choices=['draft', 'live','dead'])
    helpful = models.IntegerField(blank=True, null=True)
    not_helpful = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'help_record'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.type = self._force_type
        super().save(force_insert, force_update, using, update_fields)

class ViewRecord(HelpRecord):
    class Meta:
        proxy = True
        verbose_name = 'Page'
    _force_type = 'view'

class HelpLink(models.Model):
    help_link_id = models.AutoField(primary_key=True)
    page_url = SizedTextField(size_class=1,blank=True, null=True)
    help_record = models.OneToOneField(ViewRecord, db_column='help_record_id', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        managed = False
        db_table = 'help_link'

class FaqRecord(HelpRecord):
    class Meta:
        proxy = True
        verbose_name = 'FAQ'

    _force_type = 'faq'


class LookupRecord(HelpRecord):
    class Meta:
        proxy = True
        verbose_name = 'Lookup'

    _force_type = 'lookup'

class MovieRecord(HelpRecord):
    class Meta:
        proxy = True
        verbose_name = 'Movie'

    _force_type = 'movie'
