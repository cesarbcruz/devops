# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-04 23:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('continuousdelivery', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServerJboss',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=200)),
                ('jboss_home', models.CharField(max_length=500)),
                ('erp_home', models.CharField(max_length=500)),
                ('folder_version', models.CharField(max_length=200)),
                ('user_ssh', models.CharField(max_length=200)),
                ('password_ssh', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name': 'Server Jboss',
                'verbose_name_plural': 'Servers Jboss',
            },
        ),
    ]