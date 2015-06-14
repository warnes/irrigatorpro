# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0006_auto_20150603_2146'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='probe',
            name='field',
        ),
        migrations.AddField(
            model_name='probereading',
            name='comment',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='probereading',
            name='ignore',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='probereading',
            name='irrigation',
            field=models.DecimalField(default=0.0, verbose_name=b'irrigation in inches', max_digits=4, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='probereading',
            name='max_temp_24_hours',
            field=models.DecimalField(null=True, verbose_name=b'Maximum temperature in last 24 hours', max_digits=5, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='probereading',
            name='min_temp_24_hours',
            field=models.DecimalField(null=True, verbose_name=b'Minimum temperature in last 24 hours', max_digits=5, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='probereading',
            name='rain',
            field=models.DecimalField(default=0.0, verbose_name=b'rainfall in inches', max_digits=4, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='waterhistory',
            name='ignore',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='waterhistory',
            name='max_temp_24_hours',
            field=models.DecimalField(null=True, verbose_name=b'Maximum temperature in last 24 hours', max_digits=5, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='waterhistory',
            name='min_temp_24_hours',
            field=models.DecimalField(null=True, verbose_name=b'Minimum temperature in last 24 hours', max_digits=5, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='waterhistory',
            name='soil_potential_16',
            field=models.DecimalField(default=0.0, null=True, max_digits=5, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='waterhistory',
            name='soil_potential_24',
            field=models.DecimalField(default=0.0, null=True, max_digits=5, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='waterhistory',
            name='soil_potential_8',
            field=models.DecimalField(default=0.0, null=True, max_digits=5, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='probereading',
            name='soil_potential_16',
            field=models.DecimalField(default=0.0, null=True, max_digits=5, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='probereading',
            name='soil_potential_24',
            field=models.DecimalField(default=0.0, null=True, max_digits=5, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='probereading',
            name='soil_potential_8',
            field=models.DecimalField(default=0.0, null=True, max_digits=5, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterhistory',
            name='irrigation',
            field=models.DecimalField(default=0.0, verbose_name=b'irrigation in inches', max_digits=4, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterhistory',
            name='rain',
            field=models.DecimalField(default=0.0, verbose_name=b'rainfall in inches', max_digits=4, decimal_places=2, blank=True),
            preserve_default=True,
        ),
    ]
