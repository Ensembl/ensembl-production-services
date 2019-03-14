# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import *


class ProductionModelAdmin(admin.ModelAdmin):
    list_per_page = 50
    readonly_fields = ('modified_by', 'created_by', 'created_at', 'modified_at')

class AttribInline(admin.TabularInline):
    model = MasterAttrib
    extra = 1
    fields = ['value', 'modified_by', 'created_by', 'created_at', 'modified_at']
    readonly_fields = ('modified_by', 'created_by', 'created_at', 'modified_at')

class AttribSetInline(admin.TabularInline):
    model = MasterAttribSet
    extra = 1
    fields = ['attrib_set_id', 'modified_by', 'created_by', 'created_at', 'modified_at']
    readonly_fields = ('modified_by', 'created_by', 'created_at', 'modified_at')

class AnalysisDescriptionInline(admin.TabularInline):
    model = AnalysisDescription
    extra = 1
    fields = ['logic_name', 'display_label', 'description', 'web_data', 'db_version', 'displayable']
    readonly_fields = ('modified_by', 'created_by', 'created_at', 'modified_at')

# Register your models here.
class AttribTypeAdmin(ProductionModelAdmin):
    list_display = ('code', 'name','description')
    search_fields = ('code', 'name','description')
    inlines = (AttribInline, )

class AttribAdmin(ProductionModelAdmin):
    list_display = ('value','attrib_type')
    search_fields = ('value','attrib_type__name')
    inlines = (AttribSetInline, )


class AttribSetAdmin(ProductionModelAdmin):
   list_display = ('attrib','attrib_set_id')
   search_fields = ('attrib__value','attrib_set_id')

class BioTypeAdmin(ProductionModelAdmin):
    list_display = ('name','object_type','db_type','biotype_group','attrib_type','is_dumped','description')
    search_fields = ('name','object_type','db_type','biotype_group','attrib_type__name','description')

class AnalysisDescriptionAdmin(ProductionModelAdmin):
    list_display = ('logic_name', 'display_label', 'description', 'web_data', 'db_version', 'displayable')
    search_fields = ('logic_name', 'display_label', 'description','web_data__data')

class MetakeyAdmin(ProductionModelAdmin):
    list_display = ('name','is_optional','db_type','description')
    search_fields = ('name','db_type','description')

class WebDataAdmin(ProductionModelAdmin):
    list_display = ('data','comment')
    search_fields = ('data','comment')
    inlines = (AnalysisDescriptionInline, )


class MasterExternalDbAdmin(ProductionModelAdmin):
    list_display = ('db_name','db_release','status','db_display_name','priority','type','secondary_db_name','secondary_db_table')
    search_fields = ('db_name','db_release','status','db_display_name','priority','type','secondary_db_name','secondary_db_table')

admin.site.register(AnalysisDescription, AnalysisDescriptionAdmin)
admin.site.register(MasterAttribType, AttribTypeAdmin)
admin.site.register(MasterAttrib, AttribAdmin)
admin.site.register(MasterAttribSet, AttribSetAdmin)
admin.site.register(MasterBiotype, BioTypeAdmin)
admin.site.register(MetaKey, MetakeyAdmin)
admin.site.register(WebData, WebDataAdmin)
admin.site.register(MasterExternalDb, MasterExternalDbAdmin)