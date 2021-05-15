# Generated by Django 2.2.7 on 2019-11-22 12:59
from django.core.management import call_command
from django.db import migrations
from django.conf import settings


def load_fixture(apps, schema_editor):
    if 'sitetree' in settings.INSTALLED_APPS:
        call_command('loaddata', 'treedump', app_label='ensembl_prodinf_portal')


class Migration(migrations.Migration):

    @classmethod
    @property
    def dependencies(cls):
        deps = [('ensembl_prodinf_portal', '0003_auto_20190919_1325'),]
        if 'sitetree' in settings.INSTALLED_APPS:
            deps.append(('sitetree', '0001_initial'))
        return deps

    operations = [
        migrations.RunPython(load_fixture),
    ]