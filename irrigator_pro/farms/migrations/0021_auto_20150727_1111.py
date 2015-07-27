# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf        import settings
from django.db          import models, migrations
from django.utils       import timezone

from farms.models       import *

def probe_reading_to_water_history(apps, schema_editor):

    """
    Take the FieldDataReading part of the ProbeReadings and create
    WaterHistory objects with the same date, and source UGA"
    """


    ProbeReading = apps.get_model("farms", "ProbeReading")
    Probe = apps.get_model("farms", "Probe")

    probe_query = Probe.objects.all()
    probe_reading_query = ProbeReading.objects.all()

    for probe in probe_query:
        for probe_reading in probe_reading_query.filter(radio_id = probe.radio_id):
            wh = WaterHistory(
                source                  = "UGA",
                crop_season_id          = probe.crop_season_id,
                field_id                = probe.field_id,
                datetime                = probe_reading.datetime,
                max_temp_24_hours       = probe_reading.max_temp_24_hours,
                min_temp_24_hours       = probe_reading.min_temp_24_hours,
                soil_potential_8        = probe_reading.soil_potential_8,
                soil_potential_16       = probe_reading.soil_potential_16,
                soil_potential_24       = probe_reading.soil_potential_24,
                rain                    = probe_reading.rain,
                irrigation              = probe_reading.irrigation,
                muser_id                = probe_reading.muser_id,
                cuser_id                = probe_reading.cuser_id,
                mdate                   = timezone.now()
            )
            wh.save()
        ## Don't set ignore since it means nothing here.
    
    


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0020_remove_available_water_content__add_source'),
    ]

    operations = [
        migrations.RunPython(probe_reading_to_water_history),
    ]
