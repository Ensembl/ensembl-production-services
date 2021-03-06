# Generated by Django 2.1.7 on 2019-09-24 15:13

from django.conf import settings
from django.db import migrations
import django.db.models.deletion
import ensembl_production.models


class Migration(migrations.Migration):

    dependencies = [
        ('ensembl_website', '0002_auto_20190919_1325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='helprecord',
            name='created_by',
            field=ensembl_production.models.SpanningForeignKey(blank=True, db_column='created_by', db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='helprecord_created_by', related_query_name='helprecord_creates', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='helprecord',
            name='modified_by',
            field=ensembl_production.models.SpanningForeignKey(blank=True, db_column='modified_by', db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='helprecord_modified_by', related_query_name='helprecord_updates', to=settings.AUTH_USER_MODEL),
        ),
    ]
