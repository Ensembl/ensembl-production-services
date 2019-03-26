# -*- coding: utf-8 -*-
from django.contrib import admin


class ProductionUserAdminMixin(admin.ModelAdmin):
    """ Mixin class to assiciated request user to integer ID in another database host
    Allow cross linking within multiple database
    Warning: Do not check for foreign key integrity across databases
    """

    def save_model(self, request, obj, form, change):
        if change:
            if form.changed_data:
                obj.modified_by = request.user
        else:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
