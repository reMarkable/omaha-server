# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2020-03-02 15:23
from __future__ import unicode_literals

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0033_auto_20171020_0919'),
    ]

    operations = {
        # Create the new `channels` field:
        migrations.AddField(
            model_name='version',
            name='channels',
            field=models.ManyToManyField(db_index=True, to='omaha.Channel'),
        ),
        # Migrate to the new channels field. Would be nice to do this from
        # Python / Django, but VersionField seems to have a bug that leads to
        # exceptions when doing Version.objects.all() in a RunPython migration.
        migrations.RunSQL("""
            INSERT INTO versions_channels(version_id, channel_id)
            SELECT id, channel_id FROM versions
        """)
    }
