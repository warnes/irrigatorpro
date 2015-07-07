# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0009_add_waterhistory_datetime_and_copy_date')
    ]

    operations = [
        migrations.RenameField(
            model_name='probereading',
            old_name='reading_datetime',
            new_name='datetime',
        ),
    ]
