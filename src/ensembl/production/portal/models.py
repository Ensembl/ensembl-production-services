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
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.staticfiles import finders
from django.core.exceptions import ValidationError
from django.db import models
from django.db.utils import ConnectionHandler, ConnectionRouter
from django.templatetags.static import static
from django.urls import reverse
from django.utils.safestring import mark_safe

from ensembl.production.djcore.models import BaseTimestampedModel

connections = ConnectionHandler()
router = ConnectionRouter()
NOT_PROVIDED = object()


class AppViewObjects(models.Manager):
    def user_apps(self, user: AbstractUser):
        if user.is_superuser:
            return self.all()
        return self.filter(app_groups__name__in=user.groups.values_list('name', flat=True)).distinct()


class ProductionApp(BaseTimestampedModel):
    class Meta:
        app_label = 'ensembl_prodinf_portal'
        verbose_name = 'App Admin'
        verbose_name_plural = 'Apps Admin'
        db_table = 'production_app'

    def __str__(self):
        return self.app_name

    color_theme = (
        ('17a2b8', 'Ensembl'),
        ('007bff', 'Metazoa'),
        ('6c757d', 'Microbes'),
        ('28a745', 'Plants'),
        ('770f31', 'Rapid'),
        ('17a2b8', 'Vertebrates'),
        ('8552c0', 'Viruses'),
        ('ff9900', 'Gifts'),
        ('17a2b8', 'Production'),
    )

    app_id = models.AutoField(primary_key=True)
    app_name = models.CharField("App display name", max_length=255, null=False)
    app_is_framed = models.BooleanField('Display app in iframe', default=True, null=True, help_text='Need an url then')
    app_url = models.URLField("App flask url", max_length=255, null=True, blank=True)
    app_theme = models.CharField(max_length=6, default='FFFFFF', choices=color_theme)
    app_groups = models.ManyToManyField(Group, blank=True)
    app_prod_url = models.CharField('App Url', max_length=200, null=False, unique=True)

    @property
    def img(self):
        if finders.find('portal/img/' + self.app_prod_url.split('-')[0] + ".png"):
            return u'portal/img/' + self.app_prod_url.split('-')[0] + ".png"
        else:
            return u'portal/img/logo_industry.png'

    @property
    def img_admin_tag(self):
        return mark_safe(u"<img class='admin_app_logo' src='" + static(self.img) + "'/>")

    @property
    def app_admin_url(self):
        return '/app/' + self.app_prod_url

    def clean(self):
        super().clean()
        if self.app_is_framed and not self.app_url:
            raise ValidationError('You must set url if app is iframed')

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.app_id,))


class AppView(ProductionApp):
    class Meta:
        proxy = True
        app_label = 'ensembl_prodinf_portal'
        verbose_name = 'Production Service'
        verbose_name_plural = 'Production Services'
        ordering = ("app_name",)

    objects = AppViewObjects()

    # TODO single entry point for supervisors
    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(AppView)
        return reverse("admin:%s_%s_change" % (content_type.app_label, 'appview'), args=(self.app_id,))