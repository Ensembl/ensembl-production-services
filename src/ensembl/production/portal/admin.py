#   See the NOTICE file distributed with this work for additional information
#   regarding copyright ownership.
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.import jsonfield

import jsonfield
from django.contrib import admin
# Unregister the provided model admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.safestring import mark_safe

from ensembl.production.djcore.admin import ProductionUserAdminMixin, SuperUserAdmin
from ensembl.production.portal.models import ProductionApp, AppView

admin.site.unregister(User)


@admin.register(ProductionApp)
class ProductionAppAdmin(ProductionUserAdminMixin, SuperUserAdmin):
    list_display = ('app_name', 'app_url', 'app_url_link', 'app_is_framed', 'img_url', 'app_theme_color')
    readonly_fields = ('img_url',
                       'app_theme_color', 'app_url_link', 'created_by', 'created_at', 'modified_at',
                       'modified_by')
    fields = ('app_name', 'app_prod_url', 'app_url_link',
              'app_is_framed', 'app_url',
              'app_theme', 'app_groups',
              ('created_by', 'created_at'),
              ('modified_by', 'modified_at'))
    ordering = ('app_name',)
    formfield_overrides = {
        jsonfield.JSONField: {'widget': jsonfield.fields.JSONWidget(attrs={'rows': 20, 'cols': 70,
                                                                           'class': 'vLargeTextField'})},
    }

    @staticmethod
    def app_theme_color(obj):
        return mark_safe(u"<div class='admin_app_theme_color' style='background:#" + obj.app_theme + "'/>")

    @staticmethod
    def app_url_link(obj):
        if obj.app_prod_url:
            url_view = reverse('admin:ensembl_prodinf_portal_appview_change',
                               args=(obj.app_id,))
            return mark_safe(u"<a href='" + url_view + "'>" + obj.app_prod_url + "</a>")
        else:
            return "N/A"

    def img_url(self, obj):
        return obj.img_admin_tag

    img_url.short_description = 'App Logo'
    img_url.allow_tags = True

    def clean_app_url(self):
        # TODO Allow relative url with automatic append of host?
        pass


@admin.register(AppView)
class ProductionAppView(admin.ModelAdmin):
    # TODO change url scheme to keep previous app/<appname>?
    list_filter = ['app_name', 'app_url']

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        # TODO change per user group
        return True

    def has_add_permission(self, request):
        return False

    def has_module_permission(self, request):
        return True

    def get_object(self, request, object_id, from_field=None):
        return super().get_object(request, object_id, from_field)

    def add_view(self, request, form_url='', extra_context=None):
        return super().add_view(request, form_url, extra_context)

    def get_queryset(self, request):
        return AppView.objects.user_apps(request.user)



@admin.register(User)
class CustomUserAdmin(UserAdmin, SuperUserAdmin):
    actions = ['deactivate_users', ]

    def has_delete_permission(self, request, obj=None):
        return False

    def deactivate_users(self, request, queryset):
        cnt = queryset.filter(is_active=True).update(is_active=False)
        self.message_user(request, 'Deactivated {} users.'.format(cnt))

    deactivate_users.short_description = 'Deactivate Users'
