# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0005_auto_20150530_2316'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='probereading',
            name='comment',
        ),
        migrations.RemoveField(
            model_name='probereading',
            name='ignore',
        ),
        migrations.RemoveField(
            model_name='probereading',
            name='irrigation',
        ),
        migrations.RemoveField(
            model_name='probereading',
            name='max_temp_24_hours',
        ),
        migrations.RemoveField(
            model_name='probereading',
            name='min_temp_24_hours',
        ),
        migrations.RemoveField(
            model_name='probereading',
            name='pressure',
        ),
        migrations.RemoveField(
            model_name='probereading',
            name='rain',
        ),
        migrations.RemoveField(
            model_name='waterhistory',
            name='ignore',
        ),
        migrations.RemoveField(
            model_name='waterhistory',
            name='max_temp_24_hours',
        ),
        migrations.RemoveField(
            model_name='waterhistory',
            name='min_temp_24_hours',
        ),
        migrations.RemoveField(
            model_name='waterhistory',
            name='pressure',
        ),
        migrations.RemoveField(
            model_name='waterhistory',
            name='soil_potential_16',
        ),
        migrations.RemoveField(
            model_name='waterhistory',
            name='soil_potential_24',
        ),
        migrations.RemoveField(
            model_name='waterhistory',
            name='soil_potential_8',
        ),
        migrations.AddField(
            model_name='probe',
            name='field',
            field=models.ForeignKey(related_name='the_field', default=None, to='farms.Field'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='probereading',
            name='soil_potential_16',
            field=models.DecimalField(default=0, max_digits=5, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='probereading',
            name='soil_potential_24',
            field=models.DecimalField(default=0, max_digits=5, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='probereading',
            name='soil_potential_8',
            field=models.DecimalField(default=0, max_digits=5, decimal_places=2),
            preserve_default=False,
        ),
    ]
