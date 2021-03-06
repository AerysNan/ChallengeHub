# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-20 02:16
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('basic', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('upvote', models.BooleanField()),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='votes_c', to='basic.Competition')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='votes_u', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='reviewmeta',
            name='msg',
            field=models.CharField(default='', max_length=256),
            preserve_default=False,
        ),
    ]
