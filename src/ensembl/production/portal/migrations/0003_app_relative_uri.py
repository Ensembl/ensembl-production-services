# Generated by Django 3.2.9 on 2021-12-01 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ensembl_prodinf_portal', '0002_alter_productionapp_table'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='appview',
            options={'ordering': ('app_name',), 'verbose_name': 'Production Service', 'verbose_name_plural': 'Production Services'},
        ),
        migrations.AlterField(
            model_name='productionapp',
            name='app_theme',
            field=models.CharField(choices=[('17a2b8', 'Ensembl'), ('007bff', 'Metazoa'), ('6c757d', 'Microbes'), ('28a745', 'Plants'), ('770f31', 'Rapid'), ('17a2b8', 'Vertebrates'), ('8552c0', 'Viruses')], default='FFFFFF', max_length=6),
        ),
        migrations.AlterField(
            model_name='productionapp',
            name='app_url',
            field=models.CharField(default='/', max_length=255, verbose_name='App flask url'),
            preserve_default=False,
        ),
    ]
