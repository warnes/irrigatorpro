# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0018_copy_waterregister_date_to_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='waterregister',
            name='datetime',
            field=models.DateTimeField(blank=False),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='waterregister',
            name='date',
        ),
    ]
