# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0013_delete_probe_and_waterhistory_without_fields'),
    ]

    operations = [

        migrations.AlterField(
            model_name='waterhistory',
            name='field',
            field=models.ForeignKey(to='farms.Field', blank=False, null=False),
        ),

        migrations.AlterField(
            model_name='probe',
            name='field',
            field=models.ForeignKey(to='farms.Field', blank=False, null=False),
        ),

    ]
