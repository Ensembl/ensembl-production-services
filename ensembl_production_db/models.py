# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import json

from django.db import models
from django.template.defaultfilters import truncatechars
from django_mysql.models import EnumField
from multiselectfield import MultiSelectField

from ensembl_production.models import BaseTimestampedModel
from ensembl_production.utils import perl_string_to_python

DB_TYPE_CHOICES_BIOTYPE = (('cdna', 'cdna'),
                           ('core', 'core'),
                           ('coreexpressionatlas', 'coreexpressionatlas'),
                           ('coreexpressionest', 'coreexpressionest'),
                           ('coreexpressiongnf', 'coreexpressiongnf'),
                           ('funcgen', 'funcgen'),
                           ('otherfeatures', 'otherfeatures'),
                           ('rnaseq', 'rnaseq'),
                           ('variation', 'variation'),
                           ('vega', 'vega'),
                           ('presite', 'presite'),
                           ('sangervega', 'sangervega'))

DB_TYPE_CHOICES_METAKEY = (('cdna', 'cdna'),
                           ('compara', 'compara'),
                           ('core', 'core'),
                           ('funcgen', 'funcgen'),
                           ('otherfeatures', 'otherfeatures'),
                           ('rnaseq', 'rnaseq'),
                           ('variation', 'variation'),
                           ('vega', 'vega'),
                           ('presite', 'presite'),
                           ('sangervega', 'sangervega'))


class HasCurrent(models.Model):
    class Meta:
        abstract = True
        app_label = 'ensembl_production_db'

    is_current = models.BooleanField(default=True)


class HasDecription(object):
    @property
    def short_description(self):
        return truncatechars(self.description, 150)


class WebData(BaseTimestampedModel, HasDecription):
    web_data_id = models.AutoField(primary_key=True)
    web_data = models.TextField(db_column='`data`', null=True)
    comment = models.TextField(blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        app_label = 'ensembl_production_db'
        db_table = 'web_data'
        verbose_name = 'WebData'

    @property
    def label(self):
        try:
            json_data = perl_string_to_python(self.web_data)
            json_pretty = json.dumps(json_data, sort_keys=True, indent=4)
            return json_pretty
        except Exception:
            pass
        return self.web_data[:50] + '...' if self.web_data else ''

    def __str__(self):
        return 'ID: {} [{}...]'.format(self.pk, self.label)


class AnalysisDescription(HasCurrent, BaseTimestampedModel, HasDecription):
    analysis_description_id = models.AutoField(primary_key=True)
    logic_name = models.CharField(unique=True, max_length=128)
    description = models.TextField(blank=True, null=True)
    display_label = models.CharField(max_length=256)
    db_version = models.BooleanField('Use DB version', default=True)
    web_data = models.ForeignKey(WebData, null=True, blank=True, on_delete=models.SET_NULL,
                                 related_name='analysis')
    displayable = models.BooleanField('Is displayed', default=True)

    class Meta:
        db_table = 'analysis_description'
        app_label = 'ensembl_production_db'

    def __str__(self):
        return 'Analysis: {} ({})'.format(self.display_label, self.logic_name)


class MasterAttribType(HasCurrent, BaseTimestampedModel, HasDecription):
    attrib_type_id = models.AutoField(primary_key=True)
    code = models.CharField(unique=True, max_length=20)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'master_attrib_type'
        app_label = 'ensembl_production_db'
        verbose_name = 'AttribType'

    def __str__(self):
        return '{}'.format(self.name)


class MasterAttrib(HasCurrent, BaseTimestampedModel):
    attrib_id = models.AutoField(primary_key=True)
    value = models.CharField(max_length=80)
    attrib_type = models.ForeignKey(MasterAttribType, db_column='attrib_type_id', null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'master_attrib'
        app_label = 'ensembl_production_db'
        verbose_name = 'Attrib'

    def __str__(self):
        return '{}'.format(self.value)


class MasterAttribSet(HasCurrent, BaseTimestampedModel):
    attrib_set_id = models.IntegerField()
    attrib = models.OneToOneField(MasterAttrib, db_column='attrib_id',
                                  on_delete=models.CASCADE, primary_key=True,
                                  related_name='related_attrib_set')

    class Meta:
        db_table = 'master_attrib_set'
        app_label = 'ensembl_production_db'
        verbose_name = 'AttribSet'


class MasterBiotype(HasCurrent, BaseTimestampedModel, HasDecription):
    biotype_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    is_dumped = models.BooleanField(default=True)
    object_type = EnumField(choices=['gene', 'transcript'], default='gene')
    db_type = MultiSelectField(choices=DB_TYPE_CHOICES_BIOTYPE, default='core')
    description = models.TextField(blank=True, null=True)
    biotype_group = EnumField(
        choices=['coding', 'pseudogene', 'snoncoding', 'lnoncoding', 'mnoncoding', 'LRG', 'undefined', 'no_group'],
        default='no_group')
    so_acc = models.CharField(max_length=64, blank=True, null=True)
    so_term = models.CharField(max_length=1023, blank=True, null=True)
    attrib_type = models.ForeignKey(MasterAttribType, db_column='attrib_type_id', blank=True, null=True,
                                    on_delete=models.SET_NULL)

    class Meta:
        db_table = 'master_biotype'
        app_label = 'ensembl_production_db'
        unique_together = (('name', 'object_type'),)
        verbose_name = 'Biotype'


class MasterExternalDb(HasCurrent, BaseTimestampedModel, HasDecription):
    external_db_id = models.AutoField(primary_key=True)
    db_name = models.CharField(max_length=100)
    db_release = models.CharField(max_length=255, blank=True, null=True)
    status = EnumField(choices=['KNOWNXREF', 'KNOWN', 'XREF', 'PRED', 'ORTH', 'PSEUDO'])
    priority = models.IntegerField()
    db_display_name = models.CharField(max_length=255)
    type = EnumField(choices=['ARRAY', 'ALT_TRANS', 'ALT_GENE', 'MISC', 'LIT', 'PRIMARY_DB_SYNONYM', 'ENSEMBL'])
    secondary_db_name = models.CharField(max_length=255, blank=True, null=True)
    secondary_db_table = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'master_external_db'
        app_label = 'ensembl_production_db'
        unique_together = (('db_name', 'db_release', 'is_current'),)
        verbose_name = 'ExternalDB'


class MasterMiscSet(HasCurrent, BaseTimestampedModel, HasDecription):
    misc_set_id = models.PositiveSmallIntegerField(primary_key=True)
    code = models.CharField(unique=True, max_length=25)
    name = models.CharField(max_length=255)
    description = models.TextField()
    max_length = models.PositiveIntegerField()

    class Meta:
        app_label = 'ensembl_production_db'
        db_table = 'master_misc_set'


class MasterUnmappedReason(HasCurrent, BaseTimestampedModel):
    unmapped_reason_id = models.AutoField(primary_key=True)
    summary_description = models.CharField(max_length=255, blank=True, null=True)
    full_description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        app_label = 'ensembl_production_db'
        db_table = 'master_unmapped_reason'

    @property
    def short_description(self):
        return truncatechars(self.summary_description, 35)


class MetaKey(HasCurrent, BaseTimestampedModel, HasDecription):
    meta_key_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True)
    is_optional = models.BooleanField(default=False)
    db_type = MultiSelectField(choices=DB_TYPE_CHOICES_METAKEY)
    description = models.TextField(blank=True, null=True)
    is_multi_value = models.BooleanField(default=False)

    class Meta:
        db_table = 'meta_key'
        app_label = 'ensembl_production_db'
