# Generated by Django 2.2.7 on 2019-11-22 12:59
from django.core.management import call_command
from django.db import migrations


def load_fixture(apps, schema_editor):
    call_command('loaddata', 'treedump', app_label='ensembl_production')


class Migration(migrations.Migration):
    dependencies = [
        ('ensembl_production', '0003_auto_20190919_1325'),
        ('sitetree', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_fixture),
    ]
