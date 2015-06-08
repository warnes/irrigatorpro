# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0003_field_earliest_changed_dependency_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='waterregister',
            name='irrigation',
            field=models.DecimalField(max_digits=4, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterregister',
            name='rain',
            field=models.DecimalField(max_digits=4, decimal_places=2, blank=True),
            preserve_default=True,
        ),
    ]
