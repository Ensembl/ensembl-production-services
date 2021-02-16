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
from django.core.management.base import BaseCommand
import os

from ensembl_intentions.models import RRBug, Intention, KnownBug
from django.template.loader import get_template


class Command(BaseCommand):
    help = 'Migrate data from previous Ensembl Metadata schema version'

    def add_arguments(self, parser):
        # Commented parameters would be enable in future releases of the export, not needed for now
        parser.add_argument('-m', '--model', type=str, required=False, help='Ticket Model to export', default="RRBug")
        parser.add_argument('-o', '--output_dir', type=str, required=False, default='.', help='Target directory')
        parser.add_argument('-f', '--filter', type=str, required=False, help='Filter query')

    def handle(self, *args, **options):
        if options['model'] == "RRBug":
            Model = RRBug
        elif options['model'] == 'Intention':
            Model = Intention
        elif options['model'] == "KnownBug":
            Model = KnownBug
        context_data = Model.objects.filter(options['filter'])
        export = get_template(Model.export_template_name)
        with open(os.path.join(options['output_dir'], Model.export_file_name), 'w') as f:
            f.write(export.render({'intentions': context_data}))
