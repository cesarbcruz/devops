# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-09 13:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='vpn_password',
            field=models.CharField(blank=True, max_length=100, verbose_name='VPN password'),
        ),
        migrations.AddField(
            model_name='user',
            name='vpn_user',
            field=models.CharField(blank=True, max_length=100, verbose_name='VPN user'),
        ),
    ]