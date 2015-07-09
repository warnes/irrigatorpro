# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0019_make_waterregister_datetime_non_null_delete_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='waterhistory',
            name='available_water_content',
        ),
        migrations.AddField(
            model_name='waterhistory',
            name='source',
            field=models.CharField(default=b'Unknown', 
                                   max_length=8, 
                                   choices=[(b'UGADB', b'UGA Database'), 
                                            (b'User', b'User Entry'), 
                                            (b'Computed', b'Computed'), 
                                            (b'Unknown', b'Unknown')]
                                   ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='waterregister',
            name='source',
            field=models.CharField(default=b'Unknown', 
                                   max_length=8, 
                                   choices=[(b'UGADB', b'UGA Database'), 
                                            (b'User', b'User Entry'),
                                            (b'Computed', b'Computed'), 
                                            (b'Unknown', b'Unknown')]
                                   ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='probereading',
            name='source',
            field=models.CharField(default=b'Unknown', 
                                   max_length=8, 
                                   choices=[(b'UGADB', b'UGA Database'), 
                                            (b'User', b'User Entry'), 
                                            (b'Computed', b'Computed'), 
                                            (b'Unknown', b'Unknown')]),
            preserve_default=True,
        ),
    ]
