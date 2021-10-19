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
#   limitations under the License.from datetime import datetime

from django.conf.urls import include
from django.contrib import admin
from django.urls import path

from ensembl.production.portal.views import AppCssView, schema_view


urlpatterns = [
    # New apps layout urls
    path(f'api/production_db/', include('ensembl.production.masterdb.api.urls')),
    path(f'api/dbcopy/', include('ensembl.production.dbcopy.api.urls')),
    path(f'apidocs/', admin.site.admin_view(schema_view.with_ui(cache_timeout=10)), name='rest_api_docs'),
    path(f'app/<slug:app_prod_url>.css', AppCssView.as_view()),
    path(f'dbcopy/', include('ensembl.production.dbcopy.urls')),
    path(f'accounts/', include('django.contrib.auth.urls')),
    path(f'', admin.site.urls),
]

handler404 = 'ensembl.production.portal.views.handler404'
handler500 = 'ensembl.production.portal.views.handler500'
handler403 = 'ensembl.production.portal.views.handler403'
