# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-05 14:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('continuousdelivery', '0003_serverjboss_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='global_parameters',
            name='folder_archive_binaries',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
