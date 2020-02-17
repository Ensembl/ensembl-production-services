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
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.staticfiles import finders
from django.core import exceptions
from django.core.exceptions import ValidationError
from django.db import models
from django.db.utils import ConnectionHandler, ConnectionRouter

connections = ConnectionHandler()
router = ConnectionRouter()
NOT_PROVIDED = object()


class SpanningForeignKey(models.ForeignKey):

    def validate(self, value, model_instance):
        if self.remote_field.parent_link:
            return
        # Call the grandparent rather than the parent to skip validation
        super(SpanningForeignKey, self).validate(value, model_instance)
        if value is None:
            return

        using = router.db_for_read(self.remote_field.model, instance=model_instance)
        qs = self.remote_field.model._default_manager.using(using).filter(
            **{self.remote_field.field_name: value}
        )
        qs = qs.complex_filter(self.get_limit_choices_to())
        if not qs.exists():
            raise exceptions.ValidationError(
                self.error_messages['invalid'],
                code='invalid',
                params={
                    'model': self.remote_field.model._meta.verbose_name, 'pk': value,
                    'field': self.remote_field.field_name, 'value': value,
                },  # 'pk' is included for backwards compatibility
            )

    def __init__(self, model_on_other_db=None, **kwargs):
        self.model_on_other_db = model_on_other_db or kwargs.pop('to')
        kwargs['on_delete'] = models.SET_NULL
        kwargs['db_constraint'] = False
        super(SpanningForeignKey, self).__init__(self.model_on_other_db, **kwargs)

    def to_python(self, value):
        if isinstance(value, self.model_on_other_db):
            return value
        else:
            try:
                return self.model_on_other_db._default_manager.get(pk=value)
            except exceptions.ObjectDoesNotExist:
                return value

    def get_prep_value(self, value):
        if isinstance(value, self.model_on_other_db):
            value = value.pk
        return super(SpanningForeignKey, self).get_prep_value(value)

    #    def formfield(self, **kwargs):
    #        kwargs.update({'widget': forms.TextInput(attrs={'class': 'user_field', 'readonly': 'true'})})
    #        print(kwargs)
    #        return super().formfield(**{
    #            'form_class': forms.CharField,
    #            **kwargs,
    #        })

    def get_cached_value(self, instance, default=NOT_PROVIDED):
        cache_name = self.get_cache_name()
        try:
            return instance._state.fields_cache[cache_name]
        except KeyError:
            if default is NOT_PROVIDED:
                raise
            return default

    def get_db_prep_value(self, value, connection, prepared=False):
        return super().get_db_prep_value(value, connection, prepared)


class BaseTimestampedModel(models.Model):
    """
    Time stamped 'able' models objects, add fields to inherited objects
    """

    class Meta:
        abstract = True
        ordering = ['-updated', '-created']

    #: created by user (external DB ID)
    created_by = SpanningForeignKey(get_user_model(), db_column='created_by', blank=True, null=True,
                                    related_name="%(class)s_created_by",
                                    related_query_name="%(class)s_creates")
    created_at = models.DateTimeField('Created on', auto_now_add=True, editable=False, null=True)
    #: Modified by user (external DB ID)
    modified_by = SpanningForeignKey(get_user_model(), db_column='modified_by', blank=True, null=True,
                                     related_name="%(class)s_modified_by",
                                     related_query_name="%(class)s_updates")
    #: (auto_now): set each time model object is saved in database
    modified_at = models.DateTimeField('Last Update', auto_now=True, editable=False, null=True)


class ProductionFlaskApp(BaseTimestampedModel):
    class Meta:
        db_table = 'flask_app'
        app_label = 'ensembl_production'
        verbose_name = 'Production App'
        verbose_name_plural = 'Production Apps'

    def __str__(self):
        return self.app_name

    color_theme = (
        ('336', 'Ensembl'),
        ('707080', 'Bacteria'),
        ('714486', 'Protists'),
        ('407253', 'Plants'),
        ('725A40', 'Fungi'),
        ('015365', 'Metazoa'),
        ('800066', 'Datachecks')
    )

    # TODO add menu organisation
    app_id = models.AutoField(primary_key=True)
    app_name = models.CharField("App display name", max_length=255, null=False)
    app_is_framed = models.BooleanField('Display app in iframe', default=True, null=True, help_text='Need an url then')
    app_url = models.URLField("App flask url", max_length=255, null=True, blank=True)
    app_theme = models.CharField(max_length=6, default='FFFFFF', choices=color_theme)
    app_groups = models.ManyToManyField(Group, blank=True)
    app_prod_url = models.CharField('App Url', max_length=200, null=False, unique=True)
    app_config_params = models.TextField('Configuration parameters', null=True, blank=True)

    @property
    def img(self):
        if finders.find('img/' + self.app_prod_url.split('-')[0] + ".png"):
            return self.app_prod_url.split('-')[0] + ".png"
        else:
            return False

    def clean(self):
        super().clean()
        if self.app_is_framed and not self.app_url:
            raise ValidationError('You must set url if app is iframed')

