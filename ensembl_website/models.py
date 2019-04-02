# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

from ensembl_production.models import BaseTimestampedModel


class WebSiteModel(BaseTimestampedModel):
    class Meta:
        app_label = 'website'
        abstract = True


RECORD_STATUS = (
    ('Draft', 'draft'),
    ('Live', 'live'),
    ('Dead', 'dead'),
)

"""
glossary
faq
view
lookup
movie
"""


class HelpRecord(WebSiteModel):
    _force_type = ''
    help_record_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=255)
    keyword = models.CharField(max_length=255, blank=True, null=True)
    data = models.TextField()
    status = models.CharField(max_length=5, choices=RECORD_STATUS, null=False)
    helpful = models.IntegerField(blank=True, null=True)
    not_helpful = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'help_record'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.type = self._force_type
        super().save(force_insert, force_update, using, update_fields)


class HelpLink(WebSiteModel):
    help_link_id = models.AutoField(primary_key=True)
    page_url = models.TextField(blank=True, null=True)
    help_record_id = models.OneToOneField(HelpRecord, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        managed = False
        db_table = 'help_link'


class GlossaryRecord(HelpRecord):
    class Meta:
        proxy = True

    _force_type = 'glossary'


class ViewRecord(HelpRecord):
    class Meta:
        proxy = True

    _force_type = 'view'


class FaqRecord(HelpRecord):
    class Meta:
        proxy = True

    _force_type = 'faq'


class LookupRecord(HelpRecord):
    class Meta:
        proxy = True

    _force_type = 'lookup'
