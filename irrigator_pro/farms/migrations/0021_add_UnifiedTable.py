# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('farms', '0020_remove_available_water_content__add_source'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnifiedTable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cdate', models.DateTimeField(auto_now_add=True, verbose_name=b'creation date')),
                ('mdate', models.DateTimeField(auto_now=True, verbose_name=b'last modification date')),
                ('comment', models.TextField(blank=True)),
                ('source', models.CharField(default=b'Unknown', 
                                            max_length=8, 
                                            choices=[(b'UGADB', b'UGA Database'), 
                                                     (b'User', b'User Entry'), 
                                                     (b'Computed', b'Computed'), 
                                                     (b'Unknown', b'Unknown')]
                                            )
                 ),
                ('datetime', models.DateTimeField()),
                ('min_temp_24_hours', models.DecimalField(null=True, verbose_name=b'Minimum temperature in last 24 hours', max_digits=5, decimal_places=2, blank=True)),
                ('max_temp_24_hours', models.DecimalField(null=True, verbose_name=b'Maximum temperature in last 24 hours', max_digits=5, decimal_places=2, blank=True)),
                ('ignore', models.BooleanField(default=False)),
                ('soil_potential_8', models.DecimalField(default=0.0, null=True, max_digits=5, decimal_places=2, blank=True)),
                ('soil_potential_16', models.DecimalField(default=0.0, null=True, max_digits=5, decimal_places=2, blank=True)),
                ('soil_potential_24', models.DecimalField(default=0.0, null=True, max_digits=5, decimal_places=2, blank=True)),
                ('rain', models.DecimalField(default=0.0, verbose_name=b'rainfall in inches', max_digits=4, decimal_places=2, blank=True)),
                ('irrigation', models.DecimalField(default=0.0, verbose_name=b'irrigation in inches', max_digits=4, decimal_places=2, blank=True)),
                ('crop_stage', models.CharField(max_length=32)),
                ('daily_water_use', models.DecimalField(max_digits=3, decimal_places=2)),
                ('max_temp_2in', models.DecimalField(decimal_places=0, max_digits=3, blank=True, help_text=b'Maximum allowed soil tempoerature at 2 inch depth (Farenheit)', null=True, verbose_name=b'Temp threshold at 2in')),
                ('do_not_irrigate', models.BooleanField(default=False, help_text=b'Do not irrigate regardless of Average Water Content and Temperature')),
                ('message', models.TextField(blank=True)),
                ('irrigate_to_max', models.BooleanField(default=False)),
                ('average_water_content', models.DecimalField(max_digits=4, decimal_places=2)),
                ('max_observed_temp_2in', models.DecimalField(null=True, max_digits=4, decimal_places=1, blank=True)),
                ('computed_from_probes', models.BooleanField(default=False)),
                ('irrigate_flag', models.BooleanField(default=False)),
                ('too_hot_flag', models.BooleanField(default=False)),
                ('check_sensors_flag', models.BooleanField(default=False)),
                ('dry_down_flag', models.BooleanField(default=False)),
                ('irrigate_to_max_seen', models.BooleanField(default=False)),
                ('irrigate_to_max_achieved', models.BooleanField(default=False)),
                ('days_to_irrigation', models.SmallIntegerField(default=-1)),
                ('crop_season', models.ForeignKey(to='farms.CropSeason')),
                ('cuser', models.ForeignKey(related_name='farms_unifiedtable_cusers', verbose_name=b'creator', to=settings.AUTH_USER_MODEL)),
                ('field', models.ForeignKey(to='farms.Field')),
                ('muser', models.ForeignKey(related_name='farms_unifiedtable_musers', verbose_name=b'last modifcation user', to=settings.AUTH_USER_MODEL)),
                ('probereading', models.ForeignKey(to='farms.ProbeReading', blank=True)),
                ('waterhistory', models.ForeignKey(to='farms.WaterHistory', blank=True)),
                ('waterregister', models.ForeignKey(to='farms.WaterRegister')),
            ],
            options={
                'ordering': ('crop_season', 'field', 'source', 'datetime'),
                'verbose_name': 'Unified Table Entry',
                'verbose_name_plural': 'Unified Table Entries',
            },
            bases=(models.Model,),
        ),

        migrations.AlterUniqueTogether(
            name='unifiedtable',
            unique_together=set([('crop_season', 'field', 'source', 'datetime')]),
        ),

    ]
