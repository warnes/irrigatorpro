# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0010_rename_probereading_readingdatetime_to_datetime'),
    ]

    operations = [

        migrations.AddField(
            model_name='waterhistory',
            name='field',
            field=models.ForeignKey(to='farms.Field', blank=True, null=True),
        ),

        migrations.AddField(
            model_name='probe',
            name='field',
            field=models.ForeignKey(to='farms.Field', blank=True, null=True),
        ),

        

    ]
