# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2020-06-24 12:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0039_longer_os_platform'),
    ]

    operations = [
        migrations.AddField(
            model_name='version',
            name='allowed_user_ids',
            field=models.TextField(blank=True),
        )
    ]
