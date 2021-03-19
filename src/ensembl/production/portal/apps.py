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
from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import class_prepared
from django.utils.translation import gettext_lazy as _


def override_logentry(sender, **kwargs):
    from ensembl_production.models import SpanningForeignKey
    if sender.__name__ == "LogEntry":
        user = SpanningForeignKey(
            settings.AUTH_USER_MODEL,
            verbose_name=_('user'),
            db_column='user_id'
        )
        sender._meta.local_fields = [f for f in sender._meta.fields if f.name != "user"]
        user.contribute_to_class(sender, "user")


class EnsemblProductionConfig(AppConfig):
    name = 'ensembl_production'
    verbose_name = "Production Team"

    def ready(self):
        """
        Import signals
        :return: None
        """
        class_prepared.connect(override_logentry)
        pass
