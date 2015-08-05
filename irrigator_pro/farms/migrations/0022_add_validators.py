# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0021_auto_20150727_1111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='probereading',
            name='irrigation',
            field=models.DecimalField(decimal_places=2, default=0.0, validators=[django.core.validators.MinValueValidator(Decimal('0'))], max_digits=4, blank=True, verbose_name=b'Irrigation in inches'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='probereading',
            name='max_temp_24_hours',
            field=models.DecimalField(null=True, verbose_name=b'Maximum temperature in last 24 hours in degrees Farenheit', max_digits=5, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='probereading',
            name='min_temp_24_hours',
            field=models.DecimalField(null=True, verbose_name=b'Minimum temperature in last 24 hours in degrees Farenheit', max_digits=5, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='probereading',
            name='rain',
            field=models.DecimalField(decimal_places=2, default=0.0, validators=[django.core.validators.MinValueValidator(Decimal('0'))], max_digits=4, blank=True, verbose_name=b'Rainfall in inches'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='probereading',
            name='soil_potential_16',
            field=models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0')), django.core.validators.MaxValueValidator(Decimal('200'))]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='probereading',
            name='soil_potential_24',
            field=models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0')), django.core.validators.MaxValueValidator(Decimal('200'))]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='probereading',
            name='soil_potential_8',
            field=models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0')), django.core.validators.MaxValueValidator(Decimal('200'))]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='probereading',
            name='source',
            field=models.CharField(default=b'User', max_length=8, choices=[(b'UGA', b'UGA Database'), (b'User', b'User Entry'), (b'Computed', b'Computed'), (b'Unknown', b'Unknown')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterhistory',
            name='irrigation',
            field=models.DecimalField(decimal_places=2, default=0.0, validators=[django.core.validators.MinValueValidator(Decimal('0'))], max_digits=4, blank=True, verbose_name=b'Irrigation in inches'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterhistory',
            name='max_temp_24_hours',
            field=models.DecimalField(null=True, verbose_name=b'Maximum temperature in last 24 hours in degrees Farenheit', max_digits=5, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterhistory',
            name='min_temp_24_hours',
            field=models.DecimalField(null=True, verbose_name=b'Minimum temperature in last 24 hours in degrees Farenheit', max_digits=5, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterhistory',
            name='rain',
            field=models.DecimalField(decimal_places=2, default=0.0, validators=[django.core.validators.MinValueValidator(Decimal('0'))], max_digits=4, blank=True, verbose_name=b'Rainfall in inches'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterhistory',
            name='soil_potential_16',
            field=models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0')), django.core.validators.MaxValueValidator(Decimal('200'))]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterhistory',
            name='soil_potential_24',
            field=models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0')), django.core.validators.MaxValueValidator(Decimal('200'))]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterhistory',
            name='soil_potential_8',
            field=models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0')), django.core.validators.MaxValueValidator(Decimal('200'))]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterhistory',
            name='source',
            field=models.CharField(default=b'User', max_length=8, choices=[(b'UGA', b'UGA Database'), (b'User', b'User Entry'), (b'Computed', b'Computed'), (b'Unknown', b'Unknown')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterregister',
            name='irrigation',
            field=models.DecimalField(decimal_places=2, default=0.0, validators=[django.core.validators.MinValueValidator(Decimal('0'))], max_digits=4, blank=True, verbose_name=b'Irrigation in inches'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterregister',
            name='max_temp_24_hours',
            field=models.DecimalField(null=True, verbose_name=b'Maximum temperature in last 24 hours in degrees Farenheit', max_digits=5, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterregister',
            name='min_temp_24_hours',
            field=models.DecimalField(null=True, verbose_name=b'Minimum temperature in last 24 hours in degrees Farenheit', max_digits=5, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterregister',
            name='rain',
            field=models.DecimalField(decimal_places=2, default=0.0, validators=[django.core.validators.MinValueValidator(Decimal('0'))], max_digits=4, blank=True, verbose_name=b'Rainfall in inches'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterregister',
            name='soil_potential_16',
            field=models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0')), django.core.validators.MaxValueValidator(Decimal('200'))]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterregister',
            name='soil_potential_24',
            field=models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0')), django.core.validators.MaxValueValidator(Decimal('200'))]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterregister',
            name='soil_potential_8',
            field=models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0')), django.core.validators.MaxValueValidator(Decimal('200'))]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterregister',
            name='source',
            field=models.CharField(default=b'User', max_length=8, choices=[(b'UGA', b'UGA Database'), (b'User', b'User Entry'), (b'Computed', b'Computed'), (b'Unknown', b'Unknown')]),
            preserve_default=True,
        ),
    ]
