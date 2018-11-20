# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-20 09:00
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('basic', '0002_auto_20181120_1016'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vote',
            name='upvote',
        ),
        migrations.AddField(
            model_name='vote',
            name='status',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='vote',
            name='competition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='competition_votes', to='basic.Competition'),
        ),
        migrations.AlterField(
            model_name='vote',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='user_votes', to=settings.AUTH_USER_MODEL),
        ),
    ]
