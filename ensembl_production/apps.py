# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.conf import settings
from django.db import models
from django.db.models.signals import class_prepared
from django.utils.translation import gettext_lazy as _

from ensembl_production.models import SpanningForeignKey


def override_logentry(sender, **kwargs):
    if sender.__name__ == "LogEntry":
        user = SpanningForeignKey(
            settings.AUTH_USER_MODEL,
            models.SET_NULL,
            verbose_name=_('user'),
            db_constraint=False
        )
        sender._meta.local_fields = [f for f in sender._meta.fields if f.name != "user"]
        user.contribute_to_class(sender, "user")


class_prepared.connect(override_logentry)


class EnsemblProductionUserConfig(AppConfig):
    name = 'ensembl_production'

    def ready(self):
        """
        Import signals
        :return: None
        """
        pass
