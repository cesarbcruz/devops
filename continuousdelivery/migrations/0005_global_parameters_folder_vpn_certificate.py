# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-09 02:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('continuousdelivery', '0004_global_parameters_folder_archive_binaries'),
    ]

    operations = [
        migrations.AddField(
            model_name='global_parameters',
            name='folder_vpn_certificate',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
