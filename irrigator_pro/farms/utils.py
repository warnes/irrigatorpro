from farms.models import *
import datetime

def get_probe_readings(crop_season, field, start_date = None, end_date = None):
 
 
 
    probes = Probe.objects.filter(crop_season=crop_season, field_list=field).all()
    radio_ids = []
    if probes is None or len(probes) == 0:
        return None
    else:
        for probe in probes:
            radio_ids.append(probe.radio_id)
    
    # Make sure radio ids are unique
    radio_ids = list(set(radio_ids))


    ## Collect all the probe readings: for each radio ID keep one only one probe reading 
    ## from the date sent as parameter. If there is more than one keep the latest.

    if start_date is None:
        start_date = crop_season.season_start_date
        
    if end_date is None:
        end_date = min(date.today(), crop_season.season_end_date)


    probe_readings = []
    for r_id in radio_ids:
        probe_reading = ProbeReading.objects.filter(radio_id=r_id,
                                                    reading_datetime__startswith=start_date,
                                                    reading_datetime__endswith = end_date).order_by('reading_datetime').all()

        if  probe_reading:
            probe_readings.append(probe_reading)

    return probe_readings
