# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0007_auto_20150614_1333'),
    ]

    operations = [
        migrations.AddField(
            model_name='waterhistory',
            name='reading_time',
            field=models.TimeField(default='00:00'),
            preserve_default=False,
        ),
    ]
