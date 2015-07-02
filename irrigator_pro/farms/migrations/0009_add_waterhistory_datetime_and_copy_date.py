# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from datetime import date, datetime

class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0008_waterhistory_reading_time'),
    ]

    operations = [
        migrations.RenameField(
            model_name='waterhistory',
            old_name='date',
            new_name='datetime'
        ),
        migrations.AlterField(
            model_name='waterhistory',
            name='datetime',
            field=models.DateTimeField(),
            preserve_default=True
        ),
    ]
