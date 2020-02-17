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
import random

from django.core.exceptions import PermissionDenied
from django.shortcuts import render_to_response
from django.views.generic import DetailView

from .models import ProductionFlaskApp


class FlaskAppView(DetailView):
    template_name = "app/iframe.html"
    model = ProductionFlaskApp
    context_object_name = 'flask_app'
    queryset = ProductionFlaskApp.objects.all()
    slug_field = 'app_prod_url'
    slug_url_kwarg = "app_prod_url"
    object = None

    def get_context_data(self, **kwargs):
        kwargs.update({
            'url_cache': random.random(),
            'flask_img': self.object.img
        })
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if "Production" in self.object.app_groups.values_list('name', flat=True) and not (
                self.request.user.is_authenticated and self.request.user.is_superuser):
            raise PermissionDenied()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_template_names(self):
        if self.object and self.object.app_is_framed:
            return ["app/iframe.html"]
        else:
            return ["app/index.html"]


class AngularView(FlaskAppView):
    template_name = "app/index.html"


class AngularConfigView(FlaskAppView):
    template_name = "app/config.js.tpl"
    content_type = 'application/javascript'

    def get_context_data(self, **kwargs):
        kwargs.update({
            "config": {
                'LIVE_URI': 'mysql://ensro@mysql-eg-publicsql:4157/',
                'STAGING_URI': 'mysql://ensro@mysql-ens-sta-3:4160/',
                'COMPARA_URI': 'mysql://ensro@mysql-eg-pan-prod:4276/ensembl_compara_master',
                'PROD_URI': 'mysql://ensro@mysql-ens-meta-prod-1:4483/ensembl_production',
                'HC_SRV_URL': 'http://production-services.ensembl.org/api/production/hc/',
                'DB_SRV_URL': 'http://production-services.ensembl.org/api/production/db/',
                'URI_USER': 'ensro',
                'COPY_SOURCE_USER': 'ensro',
                'COPY_TARGET_USER': 'ensrw',
                'DATA_FILES_PATH': '/nfs/panda/ensembl/production/ensemblftp/data_files/',
                'METADATA_SRV_URL': '/api/production/meta/',
                'HANDOVER_SRV_URL': '/api/production/ho/',
                'WEBSITE_NAME': 'Non-Vertebrates !'
            }})

        return super().get_context_data(**kwargs)

    def get_template_names(self):
        return [self.template_name]


def handler404(request, *args, **argv):
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response


def handler500(request, *args, **argv):
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response


def handler403(request, *args, **argv):
    print('in here')
    response = render_to_response('403.html', {})
    response.status_code = 403
    return response
