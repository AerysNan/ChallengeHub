# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-30 02:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basic', '0004_auto_20181030_1021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='commit_filepath',
            field=models.FilePathField(blank=True),
        ),
    ]