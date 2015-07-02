# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0015_probe_waterhistory_remove_field_list'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='waterhistory',
            name='reading_time',
        ),
    ]
