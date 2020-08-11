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
from django_mysql.models import EnumField, SizedTextField
from django import forms

from ensembl_production.models import BaseTimestampedModel

"""
faq
view
lookup
movie
"""
DIVISION_CHOICES = [
    #(None, '----'),
    ('bacteria', 'Bacteria'),
    ('fungi', 'Fungi'),
    ('metazoa', 'Metazoa'),
    ('plants', 'Plants'),
    ('protists', 'Protists'),
    ('vertebrates', 'Vertebrates'),
    ('viruses', 'Viruses')
]


class HelpRecord(BaseTimestampedModel):
    class Meta:
        db_table = 'help_record'
        app_label = 'ensembl_website'

    _force_type = ''
    help_record_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=255)
    keyword = SizedTextField(size_class=1, blank=True, null=True)
    data = models.TextField()
    status = EnumField(choices=[('draft', 'Draft'), ('live', 'Live'), ('dead', 'Dead')])
    helpful = models.IntegerField(blank=True, null=True)
    not_helpful = models.IntegerField(blank=True, null=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.type = self._force_type
        super().save(force_insert, force_update, using, update_fields)


class ViewRecord(HelpRecord):
    class Meta:
        proxy = True
        verbose_name = 'Page'
        app_label = 'ensembl_website'

    _force_type = 'view'


class HelpLink(models.Model):
    class Meta:
        db_table = 'help_link'
        app_label = 'ensembl_website'

    help_link_id = models.AutoField(primary_key=True)
    page_url = SizedTextField(size_class=1, null=True)
    help_record = models.OneToOneField(ViewRecord, db_column='help_record_id', blank=True, null=True,
                                       on_delete=models.CASCADE)


class FaqRecord(HelpRecord):
    class Meta:
        proxy = True
        verbose_name = 'FAQ'
        app_label = 'ensembl_website'

    _force_type = 'faq'


class LookupRecord(HelpRecord):
    class Meta:
        proxy = True
        verbose_name = 'Lookup'
        app_label = 'ensembl_website'

    _force_type = 'lookup'


class MovieRecord(HelpRecord):
    class Meta:
        proxy = True
        verbose_name = 'Movie'
        app_label = 'ensembl_website'

    _force_type = 'movie'
