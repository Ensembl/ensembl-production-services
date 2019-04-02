from django import forms
from django.contrib import admin

from admin import ProductionUserAdminMixin
from ensembl_production.utils import list_to_perl_string, perl_string_to_python, to_internal_value
from .models import *


class WebSiteRecordForm(forms.ModelForm):
    class Meta:
        exclude = ('type', 'data')


class GlossaryForm(WebSiteRecordForm):
    ex_word = forms.CharField(label="Word")
    ex_expanded = forms.CharField(label="Expanded")
    ex_meaning = forms.CharField(label="Meaning", widget=forms.Textarea({'rows': 20}))


class WebsiteModelAdmin(ProductionUserAdminMixin):
    list_per_page = 50
    readonly_fields = ('created_by', 'created_at', 'modified_by', 'modified_at', 'helpful', 'not_helpful')
    ordering = ('-modified_at', '-created_at')
    list_filter = ['created_by', 'modified_by']

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

    def save_model(self, request, obj, form, change):
        extra_field = {field[3:]: form.cleaned_data[field] for field in form.fields if field.startswith('ex_')}
        print(extra_field)
        obj.data = to_internal_value(extra_field)
        super().save_model(request, obj, form, change)


@admin.register(GlossaryRecord)
class GlossaryItemAdmin(WebsiteModelAdmin):
    form = GlossaryForm

    def get_queryset(self, request):
        q = GlossaryRecord.objects.filter(type='glossary')
        ordering = self.get_ordering(request)
        if ordering:
            q = q.order_by(*ordering)
        return q

    def get_form(self, request, obj=None, change=False, **kwargs):
        if obj:
            print('initial', obj.data)
            raw_data = perl_string_to_python(obj.data)
            print(raw_data)
            kwargs['fields'] = {'ex_' + key :val for key, val in raw_data.items()}
        print(kwargs['fields'])
        return super().get_form(request, obj, change, **kwargs)


