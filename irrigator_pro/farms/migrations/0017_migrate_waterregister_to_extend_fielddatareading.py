# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0016_waterhistory_remove_reading_time'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='waterregister',
            options={'ordering': ('crop_season', 'field', 'datetime'), 'verbose_name': 'Water Register'},
        ),
        migrations.AddField(
            model_name='waterregister',
            name='comment',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='waterregister',
            name='datetime',
            field=models.DateTimeField(blank=True, null=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='waterregister',
            name='ignore',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='waterregister',
            name='max_temp_24_hours',
            field=models.DecimalField(null=True, verbose_name=b'Maximum temperature in last 24 hours', max_digits=5, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='waterregister',
            name='min_temp_24_hours',
            field=models.DecimalField(null=True, verbose_name=b'Minimum temperature in last 24 hours', max_digits=5, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='waterregister',
            name='soil_potential_16',
            field=models.DecimalField(default=0.0, null=True, max_digits=5, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='waterregister',
            name='soil_potential_24',
            field=models.DecimalField(default=0.0, null=True, max_digits=5, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='waterregister',
            name='soil_potential_8',
            field=models.DecimalField(default=0.0, null=True, max_digits=5, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterregister',
            name='irrigation',
            field=models.DecimalField(default=0.0, verbose_name=b'irrigation in inches', max_digits=4, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterregister',
            name='rain',
            field=models.DecimalField(default=0.0, verbose_name=b'rainfall in inches', max_digits=4, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='waterregister',
            unique_together=set([('crop_season', 'field', 'datetime')]),
        ),
        # migrations.RemoveField(
        #     model_name='waterregister',
        #     name='date',
        # ),
    ]
