# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-12-17 14:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0002_auto_20191217_1232'),
    ]

    operations = [
        migrations.AddField(
            model_name='choice',
            name='stu',
            field=models.CharField(default=' ', max_length=128),
        ),
    ]
