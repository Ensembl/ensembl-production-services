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
import logging

from django.contrib import admin
from django.db import IntegrityError
from django.http import HttpResponseRedirect

from .models import ProductionFlaskApp


class ProductionUserAdminMixin(admin.ModelAdmin):
    """ Mixin class to assiciated request user to integer ID in another database host
    Allow cross linking within multiple database
    Warning: Do not check for foreign key integrity across databases
    """
    readonly_fields = ('created_by', 'created_at', 'modified_by', 'modified_at')

    class Media:
        css = {
            'all': ('css/production_admin.css',)
        }

    def save_model(self, request, obj, form, change):
        if change:
            obj.modified_by = request.user
        else:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ProductionFlaskApp)
class FlaskAppAdmin(ProductionUserAdminMixin):
    list_display = ('app_name', 'app_url', 'app_theme', 'app_prod_url')

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_module_permission(self, request):
        return request.user.is_superuser
