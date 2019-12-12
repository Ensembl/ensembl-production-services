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
from django.conf.urls import url, include
from django.urls import path, re_path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.views import LoginView

import ensembl_production.views as views
import ensembl_dbcopy.views as CopyViews

urlpatterns = [
    # Production Admin
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^admin/', admin.site.urls),
    url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
    path('dbcopy/submit/', CopyViews.SubmitView.as_view()),
    path('dbcopy/<uuid:job_id>/', CopyViews.JobView.as_view(), name='detail'),
    path('dbcopy/list/', CopyViews.JobListView.as_view(), name='list'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', RedirectView.as_view(url='/app/admin/login', permanent=True), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    # Production DB API
    url(r'^api/production_db/', include('ensembl_production_db.api.urls')),
    url(r'^api/dbcopy/', include('ensembl_dbcopy.api.urls')),
    re_path(r'^app/(?P<app_prod_url>[a-z\-]+)/.*$', views.FlaskAppView.as_view()),
]

handler404 = 'ensembl_production.views.handler404'
handler500 = 'ensembl_production.views.handler500'
handler403 = 'ensembl_production.views.handler403'

admin.site.site_header = "Ensembl Production Services"
admin.site.site_title = "Ensembl Production Services"
admin.site.index_title = "Welcome to Ensembl Production Services"
