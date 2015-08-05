# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0024_rain_and_irrigation_allow_null'),
    ]

    operations = [
        migrations.AlterField(
            model_name='probereading',
            name='irrigation',
            field=models.DecimalField(decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0'))], max_digits=4, blank=True, null=True, verbose_name=b'Irrigation in inches'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='probereading',
            name='rain',
            field=models.DecimalField(decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0'))], max_digits=4, blank=True, null=True, verbose_name=b'Rainfall in inches'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterhistory',
            name='irrigation',
            field=models.DecimalField(decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0'))], max_digits=4, blank=True, null=True, verbose_name=b'Irrigation in inches'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterhistory',
            name='rain',
            field=models.DecimalField(decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0'))], max_digits=4, blank=True, null=True, verbose_name=b'Rainfall in inches'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterregister',
            name='irrigation',
            field=models.DecimalField(decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0'))], max_digits=4, blank=True, null=True, verbose_name=b'Irrigation in inches'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterregister',
            name='rain',
            field=models.DecimalField(decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0'))], max_digits=4, blank=True, null=True, verbose_name=b'Rainfall in inches'),
            preserve_default=True,
        ),
    ]
