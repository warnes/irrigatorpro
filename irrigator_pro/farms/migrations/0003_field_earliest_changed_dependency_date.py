# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0002_auto_20150513_0054'),
    ]

    operations = [
        migrations.AddField(
            model_name='field',
            name='earliest_changed_dependency_date',
            field=models.DateField(null=True, verbose_name=b'Earliest date in modified WaterRegister dependencies', blank=True),
            preserve_default=True,
        ),
    ]
