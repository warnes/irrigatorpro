# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import sys
from django.db import connection

def convert_probe_field_list_to_field(apps, schema_editor):
   """
   For each current Probe, copy field_list[0] into field, and create
   new records for field_list[1:]

   ** For some reason, probe.field_list.all() doesn't work here, so
      use direct SQL instead. **
   """ 
   Probe = apps.get_model("farms", "Probe")

   cursor = connection.cursor()
   cursor.execute("select * from farms_probe_field_list")

   previous_id = -1
   for (id, probe_id, field_id) in cursor.fetchall():
      #print "Working on record #%d: Probe #%d, Field #%d" %(id, probe_id, field_id)
      
      """

      If there are multiple fields assigned just preserve the first one
      otherwise a unique constraing on the pair (cdop_season_id, radio_id)
      will be violated.

      This is necessary only for Alain's test server.

      """

      if probe_id != previous_id:
         previous_id = probe_id
         probe = Probe.objects.get(id=probe_id)
         if probe.field_id is None:
            probe.field_id = field_id
         else:
            probe.id = None
            probe.pk = None
            probe.field_id = field_id
            
         probe.save()

def convert_waterhistory_field_list_to_field(apps, schema_editor):
   """
   For each current WaterHistory object, copy field_list[0] into
   field, and create new records for field_list[1:]

   ** For some reason, waterhistory.field_list.all() doesn't work
      here, so use direct SQL instead. **
   """ 
   WaterHistory = apps.get_model("farms", "WaterHistory")

   cursor = connection.cursor()
   cursor.execute("select * from farms_waterhistory_field_list")
   for (id, waterhistory_id, field_id) in cursor.fetchall():
      #print "Working on ", (id, waterhistory_id, field_id)

      waterhistory = WaterHistory.objects.get(id=waterhistory_id)
      if waterhistory.field_id is None:
         waterhistory.field_id = field_id
      else:
         waterhistory.id = None
         waterhistory.pk = None
         waterhistory.field_id = field_id

      waterhistory.save()

class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0011_add_ForeignKey_for_field_to_waterhistory_and_probe'),
    ]

    operations = [

        migrations.RunPython( convert_probe_field_list_to_field ),

        migrations.RunPython( convert_waterhistory_field_list_to_field),

    ]
