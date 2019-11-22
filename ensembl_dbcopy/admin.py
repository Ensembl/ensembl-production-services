import json
from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import admin
from ensembl_dbcopy.models import *

class HostRecordForm(forms.ModelForm):
    class Meta:
        exclude = ('auto_id',)


class HostModelAdmin(admin.ModelAdmin):
    list_per_page = 50

    def has_delete_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(Host)
class HostItemAdmin(HostModelAdmin):
    form = HostRecordForm
    list_display = ('name','port','mysqld_file_owner')
    fields = ('name','port','mysqld_file_owner')
    search_fields = ('name','port','mysqld_file_owner')