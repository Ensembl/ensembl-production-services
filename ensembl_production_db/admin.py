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

import collections

from django import forms
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin import SimpleListFilter
from django.utils.safestring import mark_safe

from ensembl_production.admin import ProductionUserAdminMixin
from ensembl_production.forms import JetCheckboxSelectMultiple
from .models import *


def flatten(iter_obj):
    result = []
    for el in iter_obj:
        if isinstance(iter_obj, collections.Iterable) and not isinstance(el, str):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result


class ProductionModelAdmin(ProductionUserAdminMixin):
    list_per_page = 50
    readonly_fields = ['created_by', 'created_at', 'modified_by', 'modified_at']
    ordering = ('-modified_at', '-created_at')
    list_filter = ['created_by', 'modified_by']
    # ability to define a list of 'only_super_admin' fields
    super_user_only = []

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            flat = flatten(self.get_fields(request, obj))
            for admin_only in self.super_user_only:
                if admin_only in flat and admin_only not in readonly_fields:
                    readonly_fields += [admin_only, ]
        return readonly_fields

    def has_delete_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        if issubclass(self.model, BaseTimestampedModel):
            list_display = list_display + ('modified_at',)
        return list_display


class IsCurrentFilter(SimpleListFilter):
    title = 'Is Current'

    parameter_name = 'is_current'

    def lookups(self, request, model_admin):
        return (
            (None, 'Yes'),
            ('no', 'No'),
            ('all', 'All'),
        )

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        if self.value() == 'no':
            return queryset.filter(is_current=False)
        elif self.value() is None:
            return queryset.filter(is_current=True)


class IsDisplayableFilter(SimpleListFilter):
    title = 'Is Displayed'

    parameter_name = 'displayable'

    def lookups(self, request, model_admin):
        return (
            (None, 'Yes'),
            ('no', 'No'),
            ('all', 'All'),
        )

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        if self.value() == 'no':
            return queryset.filter(displayable=False)
        elif self.value() is None:
            return queryset.filter(displayable=True)


class ProductionTabularInline(admin.TabularInline):
    readonly_fields = ['modified_by', 'created_by', 'created_at', 'modified_at']


class AttribInline(ProductionTabularInline):
    model = MasterAttrib
    extra = 1
    fields = ('value', 'modified_by', 'created_by', 'created_at', 'modified_at')


class AttribSetInline(ProductionTabularInline):
    model = MasterAttribSet
    extra = 0
    fields = ('attrib_set_id', 'modified_by', 'created_by', 'created_at', 'modified_at')
    can_delete = True


class AnalysisDescriptionInline(ProductionTabularInline):
    model = AnalysisDescription
    extra = 0
    fields = ('logic_name', 'display_label', 'description', 'web_data', 'db_version', 'displayable')
    readonly_fields = ['logic_name', 'display_label', 'description', 'web_data', 'db_version', 'displayable']

    def has_add_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True


class HasCurrentAdmin(ProductionModelAdmin):
    list_filter = ProductionModelAdmin.list_filter + [IsCurrentFilter, ]


# Register your models here.
class AttribTypeAdmin(HasCurrentAdmin):
    list_display = ('code', 'name', 'description', 'is_current')
    fields = ('code', 'name', 'description',
              ('created_by', 'created_at'),
              ('modified_by', 'modified_at'))
    search_fields = ('code', 'name', 'description')
    inlines = (AttribInline,)


class AttribAdmin(HasCurrentAdmin):
    list_display = ('attrib_id', 'value', 'attrib_type', 'is_current')
    fields = ('value', 'attrib_type',
              ('created_by', 'created_at'),
              ('modified_by', 'modified_at'))
    # readonly_fields = ('attrib_id',)
    search_fields = ('attrib_id', 'value', 'attrib_type__name')


class AttribSetAdmin(HasCurrentAdmin):
    fields = ('attrib_set_id', 'attrib', 'is_current',
              ('created_by', 'created_at'),
              ('modified_by', 'modified_at')
              )
    list_display = ('attrib_set_id', 'attrib', 'is_current')
    search_fields = ('attrib__value', 'attrib_set_id')
    ordering = ('-modified_at',)


class BioTypeAdmin(HasCurrentAdmin):
    # TODO DBTYPE to add display inline+flex class
    fields = ('name', 'object_type', 'db_type', 'biotype_group', 'attrib_type',
              'description',
              ('is_dumped', 'is_current'),
              ('created_by', 'created_at'),
              ('modified_by', 'modified_at')
              )
    list_display = ('name', 'object_type', 'db_type', 'biotype_group', 'attrib_type', 'description', 'is_current')
    search_fields = ('name', 'object_type', 'db_type', 'biotype_group', 'attrib_type__name', 'description')


class WebDataChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        print("in here ", json.dumps(obj.data))
        return "WebData: {} - {}".format(obj.pk, json.dumps(obj.data)[:50] + '...' if obj.data else '')


class AnalysisDescriptionForm(forms.ModelForm):
    class Meta:
        model = AnalysisDescription
        exclude = ()
    web_data = WebDataChoiceField(queryset=WebData.objects.all(), required=False)


class AnalysisDescriptionAdmin(HasCurrentAdmin):
    form = AnalysisDescriptionForm
    fields = ('logic_name', 'description', 'display_label', 'web_data',
              ('db_version', 'displayable', 'is_current'),
              ('created_by', 'created_at'),
              ('modified_by', 'modified_at'))
    list_display = ('logic_name', 'short_description', 'web_data_label', 'is_current', 'displayable')
    search_fields = ('logic_name', 'display_label', 'description', 'web_data__data')

    def web_data_label(self, obj):
        return obj.web_data.label if obj.web_data else 'EMPTY'

    web_data_label.short_description = "Web Data"


class MetaKeyForm(forms.BaseModelForm):
    class Meta:
        model = MetaKey
        fields = ('__all__',)

    def __init__(self, **kwargs):
        self.fields['db_type'].widget = JetCheckboxSelectMultiple()
        super().__init__(**kwargs)


class MetakeyAdmin(HasCurrentAdmin):
    # form = MetaKeyForm
    list_display = ('name', 'is_optional', 'db_type', 'description', 'is_current')
    fields = ('name', 'description', 'db_type',
              ('is_optional', 'is_current', 'is_multi_value'),
              ('created_by', 'created_at'),
              ('modified_by', 'modified_at'))
    ordering = ('name',)
    search_fields = ('name', 'db_type', 'description')

    def get_readonly_fields(self, request, obj=None):
        read_only_fields = super().get_readonly_fields(request, obj)
        if obj is not None and 'name' not in read_only_fields:
            read_only_fields += ['name', ]
        return read_only_fields


class WebDataForm(forms.ModelForm):
    class Meta:
        model = WebData
        fields = ('data', 'comment')


class WebDataAdmin(ProductionModelAdmin):
    form = WebDataForm
    # TODO add pretty json display / conversion to Perl upon save
    list_display = ('pk', 'data_label', 'comment')
    search_fields = ('pk', 'data', 'comment')
    fields = ('data', 'comment',
              ('created_by', 'created_at'),
              ('modified_by', 'modified_at'))
    inlines = (AnalysisDescriptionInline,)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        messages.warning(request,
                         "WARNING: Updating web data with multiple analysis description update it for all of them")
        return super().change_view(request, object_id, form_url, extra_context)

    def data_label(self, obj):
        return mark_safe('<pre>' + obj.label + '</pre>') if obj else ''

    data_label.short_description = "Web Data"

    def get_queryset(self, request):
        return super().get_queryset(request)


class MasterExternalDbAdmin(HasCurrentAdmin):
    list_display = ('db_name', 'db_release', 'status', 'db_display_name', 'priority', 'type', 'secondary_db_name',
                    'secondary_db_table', 'is_current')
    fields = ('db_name', 'status', 'db_display_name', 'priority', 'type', 'db_release', 'secondary_db_name',
              'secondary_db_table', 'description',
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
