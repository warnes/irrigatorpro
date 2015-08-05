# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0022_add_validators'),
    ]

    operations = [
        migrations.AlterField(
            model_name='probereading',
            name='source',
            field=models.CharField(default=b'User', max_length=8, choices=[(b'User', b'User Entry'), (b'UGA', b'UGA Database'), (b'Computed', b'Computed'), (b'Unknown', b'Unknown')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterhistory',
            name='source',
            field=models.CharField(default=b'User', max_length=8, choices=[(b'User', b'User Entry'), (b'UGA', b'UGA Database'), (b'Computed', b'Computed'), (b'Unknown', b'Unknown')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterregister',
            name='source',
            field=models.CharField(default=b'User', max_length=8, choices=[(b'User', b'User Entry'), (b'UGA', b'UGA Database'), (b'Computed', b'Computed'), (b'Unknown', b'Unknown')]),
            preserve_default=True,
        ),
    ]
