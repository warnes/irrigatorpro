# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import farms.models


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cropseason',
            name='season_end_date',
            field=models.DateField(default=farms.models.get_default_cropseason_end, verbose_name=b'Approximate Season End Date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='cropseason',
            name='season_start_date',
            field=models.DateField(default=farms.models.get_default_cropseason_start, verbose_name=b'Season Start Date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='cropseasonevent',
            name='date',
            field=models.DateField(default=farms.models.get_default_cropseasonevent_date),
            preserve_default=True,
        ),
    ]
