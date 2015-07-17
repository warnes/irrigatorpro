# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0021_add_UnifiedTable'),
    ]

    operations = [
        migrations.AddField(
            model_name='unifiedtable',
            name='pr_datetime',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='unifiedtable',
            name='pr_source',
            field=models.CharField(default=b'Unknown', max_length=8, choices=[(b'UGADB', b'UGA Database'), (b'User', b'User Entry'), (b'Computed', b'Computed'), (b'Unknown', b'Unknown')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='unifiedtable',
            name='wh_datetime',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='unifiedtable',
            name='wh_source',
            field=models.CharField(default=b'Unknown', max_length=8, choices=[(b'UGADB', b'UGA Database'), (b'User', b'User Entry'), (b'Computed', b'Computed'), (b'Unknown', b'Unknown')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='unifiedtable',
            name='wr_datetime',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='unifiedtable',
            name='wr_source',
            field=models.CharField(default=b'Unknown', max_length=8, choices=[(b'UGADB', b'UGA Database'), (b'User', b'User Entry'), (b'Computed', b'Computed'), (b'Unknown', b'Unknown')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='probereading',
            name='source',
            field=models.CharField(default=b'Unknown', max_length=8, choices=[(b'UGADB', b'UGA Database'), (b'User', b'User Entry'), (b'Computed', b'Computed'), (b'Unknown', b'Unknown')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterhistory',
            name='source',
            field=models.CharField(default=b'Unknown', max_length=8, choices=[(b'UGADB', b'UGA Database'), (b'User', b'User Entry'), (b'Computed', b'Computed'), (b'Unknown', b'Unknown')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waterregister',
            name='source',
            field=models.CharField(default=b'Unknown', max_length=8, choices=[(b'UGADB', b'UGA Database'), (b'User', b'User Entry'), (b'Computed', b'Computed'), (b'Unknown', b'Unknown')]),
            preserve_default=True,
        ),
    ]
