# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from datetime import date, datetime, time
from django.utils.timezone import utc

def copy_date_to_datetime(apps, schema_editor):
   """
   For each current WaterRegister record, copy date into datetime
   """ 
   WaterRegister = apps.get_model("farms", "WaterRegister")

   for wr in WaterRegister.objects.all():
      print "Working on WaterRegister for Field %s for %s" % (wr.field.name, wr.date),
      wr.datetime = datetime.combine(wr.date, time(0,0))
      print " %s --> %s " % (wr.date, wr.datetime)
      wr.save()

def copy_datetime_to_date(apps, schema_editor):
   """
   For each current WaterRegister record, copy date into datetime
   """ 
   pass
   #WaterRegister = apps.get_model("farms", "WaterRegister")
   #
   #for wr in WaterRegister.objects.all():
   #    if wr.datetime:
   #        wr.date = wr.datetime.date()
   #        wr.save

class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0017_migrate_waterregister_to_extend_fielddatareading'),
    ]

    operations = [
        migrations.RunPython( copy_date_to_datetime, copy_datetime_to_date )
    ]
