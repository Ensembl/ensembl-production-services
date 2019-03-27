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
from django.core import exceptions
from django.db import models
from django.db.models.fields.related import ForeignKey
from django.db.utils import ConnectionHandler, ConnectionRouter

connections = ConnectionHandler()
router = ConnectionRouter()


class UserForeignKey(models.IntegerField):

    def __init__(self, model_on_other_db, **kwargs):
        self.model_on_other_db = model_on_other_db
        super(UserForeignKey, self).__init__(**kwargs)

    def to_python(self, value):
        if isinstance(value, self.model_on_other_db):
            return value
        else:
            return self.model_on_other_db._default_manager.get(pk=value)

    def get_prep_value(self, value):
        if isinstance(value, self.model_on_other_db):
            value = value.pk
        return super(UserForeignKey, self).get_prep_value(value)

    def get_prep_lookup(self, lookup_type, value):
        if not isinstance(value, self.model_on_other_db):
            value = self.model_on_other_db._default_manager.get(pk=value)
        return super(UserForeignKey, self).get_prep_lookup(lookup_type, value)

    def formfield(self, **kwargs):
        kwargs.update({'widget': forms.TextInput(attrs={'class': 'user_field', 'readonly': 'true'})})
        return super().formfield(**{
            'form_class': forms.CharField,
            **kwargs,
        })

    def get_db_prep_value(self, value, connection, prepared=False):
        return super().get_db_prep_value(value, connection, prepared)


NOT_PROVIDED = object()


class SpanningForeignKey(ForeignKey):

    def validate(self, value, model_instance):
        if self.remote_field.parent_link:
            return
        # Call the grandparent rather than the parent to skip validation
        super(ForeignKey, self).validate(value, model_instance)
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

    def __init__(self, model_on_other_db, **kwargs):
        self.model_on_other_db = model_on_other_db
        if 'db_contraint' in kwargs:
            kwargs['db_constraint'] = False
        kwargs['db_constraint'] = False
        super(SpanningForeignKey, self).__init__(model_on_other_db, **kwargs)

    def to_python(self, value):
        if isinstance(value, self.model_on_other_db):
            return value
        else:
            return self.model_on_other_db._default_manager.get(pk=value)

    def get_prep_value(self, value):
        if isinstance(value, self.model_on_other_db):
            value = value.pk
        return super(SpanningForeignKey, self).get_prep_value(value)

    def get_prep_lookup(self, lookup_type, value):
        if not isinstance(value, self.model_on_other_db):
            value = self.model_on_other_db._default_manager.get(pk=value)
        return super(SpanningForeignKey, self).get_prep_lookup(lookup_type, value)

    def formfield(self, **kwargs):
        kwargs.update({'widget': forms.TextInput(attrs={'class': 'user_field', 'readonly': 'true'})})
        return super().formfield(**{
            'form_class': forms.CharField,
            **kwargs,
        })

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
