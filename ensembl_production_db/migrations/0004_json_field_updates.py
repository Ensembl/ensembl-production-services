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
from django.db import migrations
import json
from ensembl_production.utils import perl_string_to_python, to_internal_value


def transform_json(apps, schema_editor):
    WebData = apps.get_model('ensembl_production_db', 'WebData')
    for record in WebData.objects.all():
        python_value = perl_string_to_python(record.web_data)
        record.web_data = json.dumps(python_value)
        record.save()


def reverse_transform_json(apps, schema_editor):
    WebData = apps.get_model('ensembl_production_db', 'WebData')
    for record in WebData.objects.all():
        perl = to_internal_value(json.loads(record.web_data))
        record.web_data = perl
        record.save()


class Migration(migrations.Migration):
    dependencies = [
        ('ensembl_production_db', '0003_auto_20191015_0945'),
    ]

    operations = [
        migrations.RunPython(transform_json, reverse_transform_json, hints={'target_db': 'ensembl_production_db'}),
    ]
