from farms.models import *
from datetime import datetime, date

from common.utils import daterange


### May not be required anymore, now that the dict is defined.

# def get_probe_readings(crop_season, field, start_date = None, end_date = None):
  
#     probes = Probe.objects.filter(crop_season=crop_season, field=field).all()
#     radio_ids = []
#     if probes is None or len(probes) == 0:
#         return None
#     else:
#         for probe in probes:
#             radio_ids.append(probe.radio_id)
    
#     # Make sure radio ids are unique
#     radio_ids = list(set(radio_ids))

#     if start_date is None:
#         start_date = crop_season.season_start_date
        
#     if end_date is None:
#         end_date = min(date.today(), crop_season.season_end_date)


#     probe_readings = []
#     for r_id in radio_ids:
#         probe_reading = ProbeReading.objects.filter(radio_id=r_id,
#                                                     datetime__gte = start_date,
#                                                     datetime__lte = end_date).order_by('datetime').all()
        
#         if  probe_reading:
#             probe_readings.extend(probe_reading.all())

#     return probe_readings




def get_probe_readings_dict(field, crop_season, start_date = None, end_date = None):

    """
    Put all probe readings in dictionary, one entry per day.
    There can be multiple probes for one day.
    """

    if start_date is None:
        start_date = crop_season.season_start_date
        
    if end_date is None:
        end_date = min(date.today(), crop_season.season_end_date)


    probe_readings = {}

    probes = Probe.objects.filter(crop_season=crop_season, field=field).all()
    if len(probes) == 0: return {}
    radio_ids = []

    for probe in probes:
        radio_ids.append(probe.radio_id)
    
    # Make sure radio ids are unique
    radio_ids = list(set(radio_ids))

    for day in daterange(start_date, end_date + timedelta(days=1)):
        for r_id in radio_ids:
            readings = ProbeReading.objects.filter(radio_id=r_id,
                                                   datetime__startswith=day).all()
            
            if len(readings) > 0:
                if day in probe_readings:
                    probe_readings[day] = probe_readings[day].append(readings)
                else:
                    probe_readings[day] = readings

    return probe_readings



def to_faren(temp_c):
    return 9.0 * temp_c /5.0 + 32.0

def to_inches(length_in_cm):
    return length_in_cm * 0.3937008


