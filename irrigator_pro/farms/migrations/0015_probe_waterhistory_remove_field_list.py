# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0014_probe_and_waterhistory_make_field_non_null'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='probe',
            name='field_list',
        ),
        migrations.RemoveField(
            model_name='waterhistory',
            name='field_list',
        ),
    ]
