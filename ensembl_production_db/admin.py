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
from django.contrib import admin

from ensembl_production.admin import ProductionUserAdminMixin
from .models import *
from django import forms
from ensembl_production.forms import JetCheckboxSelectMultiple


class ProductionModelAdmin(ProductionUserAdminMixin):
    list_per_page = 50
    readonly_fields = ('created_by', 'created_at', 'modified_by', 'modified_at')


class ProductionTabularInline(admin.TabularInline):
    readonly_fields = ('modified_by', 'created_by', 'created_at', 'modified_at')


class AttribInline(ProductionTabularInline):
    model = MasterAttrib
    extra = 1
    fields = ['value', 'modified_by', 'created_by', 'created_at', 'modified_at']


class AttribSetInline(ProductionTabularInline):
    model = MasterAttribSet
    extra = 1
    fields = ['attrib_set_id', 'modified_by', 'created_by', 'created_at', 'modified_at']


class AnalysisDescriptionInline(ProductionTabularInline):
    model = AnalysisDescription
    extra = 1
    fields = ['logic_name', 'display_label', 'description', 'web_data', 'db_version', 'displayable']


# Register your models here.
class AttribTypeAdmin(ProductionModelAdmin):
    list_display = ('code', 'name', 'description')
    fields = ('code', 'name', 'description',
              ('created_by', 'created_at'),
              ('modified_by', 'modified_at')
              )
    search_fields = ('code', 'name', 'description')
    inlines = (AttribInline,)


class AttribAdmin(ProductionModelAdmin):
    list_display = ('value', 'attrib_type')
    fields = ('value', 'attrib_type',
              ('created_by', 'created_at'),
              ('modified_by', 'modified_at'))
    search_fields = ('value', 'attrib_type__name')
    inlines = (AttribSetInline,)


class AttribSetAdmin(ProductionModelAdmin):
    fields = ('attrib_set_id', 'attrib', 'is_current',
              ('created_by', 'created_at'),
              ('modified_by', 'modified_at')
              )
    list_display = ('attrib', 'attrib_set_id')
    search_fields = ('attrib__value', 'attrib_set_id')


class BioTypeAdmin(ProductionModelAdmin):
    # TODO DBTYPE to add display inline+flex class
    fields = ('name', 'object_type', 'db_type', 'biotype_group', 'attrib_type',
              'description',
              ('is_dumped', 'is_current'),
              ('created_by', 'created_at'),
              ('modified_by', 'modified_at')
              )
    list_display = ('name', 'object_type', 'db_type', 'biotype_group', 'attrib_type', 'is_dumped', 'description')
    search_fields = ('name', 'object_type', 'db_type', 'biotype_group', 'attrib_type__name', 'description')


class AnalysisDescriptionAdmin(ProductionModelAdmin):
    fields = ('logic_name', 'description', 'display_label', 'web_data',
              ('db_version', 'displayable', 'is_current'),
              ('created_by', 'created_at'),
              ('modified_by', 'modified_at')
              )

    list_display = ('logic_name', 'display_label', 'description', 'web_data', 'db_version', 'displayable')
    search_fields = ('logic_name', 'display_label', 'description', 'web_data__data')

class MetaKeyForm(forms.BaseModelForm):
    class Meta:
        model = MetaKey
        fields = ('__all__',)

    def __init__(self, **kwargs):
        self.fields['db_type'].widget = JetCheckboxSelectMultiple()
        super().__init__(**kwargs)


class MetakeyAdmin(ProductionModelAdmin):
    form = MetaKeyForm
    list_display = ('name', 'is_optional', 'db_type', 'description')
    fields = ('name', 'description', 'is_optional', 'db_type',
              ('created_by', 'created_at'),
              ('modified_by', 'modified_at')
              )
    search_fields = ('name', 'db_type', 'description')


class WebDataAdmin(ProductionModelAdmin):
    # TODO add pretty json display / conversion to Perl upon save
    list_display = ('label', 'related_analysis', 'comment', 'pk')
    search_fields = ('data', 'comment')
    fields = ('data', 'comment',
              ('created_by', 'created_at'),
              ('modified_by', 'modified_at')
              )
    inlines = (AnalysisDescriptionInline,)

    def related_analysis(self, obj):
        return [x for x in obj.analysis.all()[:3]] if obj.analysis else 'n/a'

    related_analysis.short_description = "Analysis Description"


class MasterExternalDbAdmin(ProductionModelAdmin):
    list_display = ('db_name', 'db_release', 'status', 'db_display_name', 'priority', 'type', 'secondary_db_name',
                    'secondary_db_table')
    fields = ('db_name', 'status', 'db_display_name', 'priority', 'type', 'db_release', 'secondary_db_name',
              'secondary_db_table',
              ('created_by', 'created_at'),
              ('modified_by', 'modified_at')
              )
    search_fields = (
        'db_name', 'db_release', 'status', 'db_display_name', 'priority', 'type', 'secondary_db_name',
        'secondary_db_table')


admin.site.register(AnalysisDescription, AnalysisDescriptionAdmin)
admin.site.register(MasterAttribType, AttribTypeAdmin)
admin.site.register(MasterAttrib, AttribAdmin)
admin.site.register(MasterAttribSet, AttribSetAdmin)
admin.site.register(MasterBiotype, BioTypeAdmin)
admin.site.register(MetaKey, MetakeyAdmin)
admin.site.register(WebData, WebDataAdmin)
admin.site.register(MasterExternalDb, MasterExternalDbAdmin)
