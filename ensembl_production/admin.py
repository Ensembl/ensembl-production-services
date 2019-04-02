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


class ProductionUserAdminMixin(admin.ModelAdmin):
    """ Mixin class to assiciated request user to integer ID in another database host
    Allow cross linking within multiple database
    Warning: Do not check for foreign key integrity across databases
    """
    readonly_fields = ('created_by', 'created_at', 'modified_by', 'modified_at')

    class Media:
        css = {
            'all': ('production_admin.css',)
        }

    def save_model(self, request, obj, form, change):
        if change:
            if form.changed_data:
                obj.modified_by = request.user
        else:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        try:
            return super().change_view(request, object_id, form_url, extra_context)
        except IntegrityError as e:
            self.message_user(request, 'Error changing model: %s' % e, level=logging.ERROR)
            return HttpResponseRedirect(request.path)

    def add_view(self, request, form_url='', extra_context=None):
        try:
            return super().add_view(request, form_url, extra_context)
        except IntegrityError as e:
            self.message_user(request, 'Error changing model: %s' % e, level=logging.ERROR)
            return HttpResponseRedirect(request.path)

