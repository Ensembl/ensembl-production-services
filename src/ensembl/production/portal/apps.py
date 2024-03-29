#   See the NOTICE file distributed with this work for additional information
#   regarding copyright ownership.
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.from django.apps import AppConfig
import logging
from django.apps import AppConfig
from django.db.models.signals import class_prepared
from ensembl.production.djcore.config import override_logentry
from django.contrib.auth.apps import AuthConfig


class EnsemblProductionConfig(AppConfig):
    name = 'ensembl.production.portal'
    label = 'ensembl_prodinf_portal'
    verbose_name = "Production Team"

    def ready(self):
        """
        Import signals
        :return: None
        """
        class_prepared.connect(override_logentry)
        pass


class ProdAuthConfig(AuthConfig):
    verbose_name = "Users/Groups"
