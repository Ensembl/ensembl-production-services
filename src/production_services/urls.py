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
from datetime import datetime

from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.http import HttpResponseRedirect
from django.urls import path, re_path
from django.views import static
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView, RedirectView

import ensembl_production.views as views

urlpatterns = [
    path('',
         TemplateView.as_view(template_name='home.html', extra_context={'current_date': datetime.now()}),
         name='home'),
    path('jet/', include('jet.urls', 'jet')),  # Django JET URLS
    path('admin/', admin.site.urls),
    url('bugs/', RedirectView.as_view(url='/admin/ensembl_intentions/knownbug')),
    path('dbcopy/', include('ensembl_dbcopy.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', RedirectView.as_view(url='/admin/login', permanent=True), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('api/production_db/', include('ensembl_production_db.api.urls')),
    re_path(r'^app/(?P<app_prod_url>[a-z]+)/scripts/config.js', never_cache(views.AngularConfigView.as_view())),
    re_path(r'^app/(?P<app_prod_url>[a-z\-]+)/.*$', views.FlaskAppView.as_view(), name='production_app_view'),
    # API entries
    path('api/production_db/', include('ensembl_production_db.api.urls')),
    path('api/dbcopy/', include('ensembl_dbcopy.api.urls')),
]

if settings.DEBUG:
    urlpatterns.extend([
        url(r'^web-app/scripts/(?P<path>.*)$', static.serve,
            {'document_root': settings.BASE_DIR + "/web-app/app/scripts/"}),
        url(r'^views/(?P<path>.*)$', static.serve, {'document_root': settings.BASE_DIR + "/web-app/app/views/"}),
        url(r'^web-app/bower_components/(?P<path>.*)$', static.serve,
            {'document_root': settings.BASE_DIR + "/web-app/bower_components/"}),
    ])

handler404 = 'ensembl_production.views.handler404'
handler500 = 'ensembl_production.views.handler500'
handler403 = 'ensembl_production.views.handler403'

admin.site.site_header = "Ensembl Production Services"
admin.site.site_title = "Ensembl Production Services"
admin.site.index_title = "Welcome to Ensembl Production Services"
