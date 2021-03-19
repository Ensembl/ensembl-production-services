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

from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.http import HttpResponseRedirect
from django.urls import path, re_path
from django.views import static
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView, RedirectView
from datetime import datetime
import ensembl.production.portal.views as views

urlpatterns = [
    path('',
         TemplateView.as_view(template_name='home.html', extra_context={'current_date': datetime.now()}),
         name='home'),
    path('admin/', admin.site.urls),
    url('bugs/', RedirectView.as_view(url='/admin/ensembl_jira/knownbug')),
    path('dbcopy/', include('ensembl.production.dbcopy.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', RedirectView.as_view(url='/admin/login', permanent=True), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('api/production_db/', include('ensembl.production.masterdb.api.urls')),
    re_path(r'^app/(?P<app_prod_url>[a-z\-]+)/.*$', views.FlaskAppView.as_view(), name='production_app_view'),
    # API entries
    path('api/dbcopy/', include('ensembl.production.dbcopy.api.urls')),
]


handler404 = 'ensembl.production.portal.views.handler404'
handler500 = 'ensembl.production.portal.views.handler500'
handler403 = 'ensembl.production.portal.views.handler403'

admin.site.site_header = "Ensembl Production Services"
admin.site.site_title = "Ensembl Production Services"
admin.site.index_title = "Welcome to Ensembl Production Services"
