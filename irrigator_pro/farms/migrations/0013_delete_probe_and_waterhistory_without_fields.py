# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import sys
from django.db import connection

def delete_probe_without_field(apps, schema_editor):
   """
   Delete any Probe with null field_id
   """ 
   Probe = apps.get_model("farms", "Probe")
   
   deleted = 0
   for probe in Probe.objects.filter(field_id=None):
      probe.delete()
      deleted += 1

   print
   print "Deleted %d Probe objects with no field assigned" % deleted
   print

def delete_waterhistory_without_field(apps, schema_editor):
   """
   Delete any WaterHistory with null field_id
   """ 
   WaterHistory = apps.get_model("farms", "WaterHistory")
   
   deleted = 0
   for waterhistory in WaterHistory.objects.filter(field_id=None):
      waterhistory.delete()
      deleted += 1

   print
   print "Deleted %d WaterHistory objects with no field assigned" % deleted
   print



class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0012_copy_field_list_to_field_for_waterhistory_and_probe'),
    ]

    operations = [

        migrations.RunPython( delete_probe_without_field ),

        migrations.RunPython( delete_waterhistory_without_field ),

    ]
