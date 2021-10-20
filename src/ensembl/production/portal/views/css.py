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
from django.views.generic import DetailView

from ensembl.production.portal.models import ProductionApp


class AppCssView(DetailView):
    context_object_name = 'app'
    queryset = ProductionApp.objects.all()
    slug_field = 'app_prod_url'
    template_name = 'css.html'
    slug_url_kwarg = "app_prod_url"

    def get(self, request, *args, **kwargs):
        print(kwargs)
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return super().get_object(queryset)

    def render_to_response(self, context, **response_kwargs):
        # response = 'text/css'
        # response['Content-Disposition'] = 'attachment; filename="{}"'.format(self.model.export_file_name)
        return super().render_to_response(context, **response_kwargs)
