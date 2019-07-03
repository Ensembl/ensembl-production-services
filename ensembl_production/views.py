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
from django.core.exceptions import PermissionDenied
from django.shortcuts import render_to_response
from django.views.generic import DetailView
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import ProductionFlaskApp


class FlaskAppView(DetailView):
    template_name = "app.html"
    model = ProductionFlaskApp
    context_object_name = 'flask_app'
    queryset = ProductionFlaskApp.objects.all()
    slug_field = 'app_prod_url'
    slug_url_kwarg = "app_prod_url"

    def render_to_response(self, context, **response_kwargs):
        return super().render_to_response(context, **response_kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if "Production" in self.object.app_groups.values_list('name', flat=True) and not (
                request.user.is_authenticated and request.user.is_superuser):
            raise PermissionDenied()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


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
