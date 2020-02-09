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

from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db import models
from fernet_fields import EncryptedCharField


class Credentials(models.Model):
    class Meta:
        app_label = 'ensembl_bugs'
        verbose_name_plural = 'Credentials'

    cred_id = models.AutoField(primary_key=True)
    cred_name = models.CharField("Name", unique=True, max_length=150)
    cred_url = models.CharField("Access Url", max_length=255)
    user = models.CharField("User Name", max_length=100)
    credentials = EncryptedCharField("Password", max_length=255)
