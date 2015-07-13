from farms.models import *
from common.utils import daterange

from farms.generate_water_register import generate_water_register
from farms.utils import get_probe_readings
from django.forms.models import modelformset_factory

from django.db.models import Q

from datetime import datetime, date, timedelta

from irrigator_pro.settings import WATER_REGISTER_DELTA

# workarounds for the absence of query datetime__date operator
from common.utils import d2dt_min, d2dt_max, d2dt_range


def getDateObject(thisDate):
    '''
    Coerce argument to class date
    '''
    if thisDate is None:
        return None
    elif isinstance(thisDate, datetime):
        return thisDate.date()
    elif isinstance(thisDate, date):
        return thisDate
    else:
        return datetime.strptime(thisDate, "%Y-%m-%d").date()


"""
Returns the list of object for display in the template.
Each object is an instance of the class UnifiedReport,
defined below.
"""

def generate_objects(wh_formset, crop_season, field, user,  report_date):

    if crop_season.season_start_date > report_date:
        return None
    
    if crop_season.season_end_date < report_date:
        report_date = crop_season.season_end_date

    generate_water_register(crop_season, field, user, report_date)

    water_register_query = WaterRegister.objects.filter(crop_season = crop_season, field = field)
    water_register_query = water_register_query.order_by('-datetime')
    water_register_query = water_register_query.filter(
                               Q(datetime__lte =  d2dt_min(report_date + timedelta(WATER_REGISTER_DELTA))) 
                               )

    ### probe_readings will contain all the readings in increasing order of time.


    current_probe_reading = None
    probe_readings = get_probe_readings(crop_season, field, None, report_date)

    if probe_readings is not None and len(probe_readings) > 0:
        probe_readings.reverse()
        current_probe_reading = probe_readings.pop()
        while current_probe_reading is not None and current_probe_reading.date < crop_season.season_start_date:
            if len(probe_readings) == 0:
                current_probe_reading = None
            else:
                current_probe_reading = probe_readings.pop()


    form_index = 0
    current_form = None
    all_forms = wh_formset.forms
    ret = []

    if all_forms is not None and len(all_forms) > 0:
        current_form = all_forms[form_index]
        form_index = form_index + 1

        while current_form is not None and \
              getDateObject(current_form['datetime'].value()) is not None and \
              getDateObject(current_form['datetime'].value()) < crop_season.season_start_date:
            if form_index == len(all_forms):
                current_form = None
            else:
                current_form = all_forms[form_index]
                form_index = form_index + 1
                

    for day in daterange(crop_season.season_start_date, report_date + timedelta(days=1)):
        #try:
            water_register = water_register_query.get(datetime__range = d2dt_range(day))
            day_record = UnifiedReport(day, water_register)

            ## Next two while
            while current_probe_reading is not None and current_probe_reading.date == day:
                day_record.uga_records.append(current_probe_reading)
                if len(probe_readings) > 0:
                    current_probe_reading = probe_readings.pop()
                else:
                    current_probe_reading = None
            

            while current_form is not None and getDateObject(current_form['datetime'].value()) == day:
                day_record.forms.append(current_form)
                if form_index == len(all_forms):
                    current_form = None
                else:
                    current_form = all_forms[form_index]
                    form_index = form_index + 1

            ret.append(day_record)
            
        #except BaseException as x:
        #    return None


    # Add records for days in the future
    
    ### Might want days=WATER_REGISTER_DELTA+1 below, but we don't do it
    ### in generate_water_register

    ### Also this loop could be merges with above. But this is easier to see
    ### what happens
    report_plus_delta = min(report_date + timedelta(days=WATER_REGISTER_DELTA), crop_season.season_end_date)
    
    for day in daterange(report_date + timedelta(days=1), report_plus_delta):
        water_register = water_register_query.get(datetime__range = d2dt_range(day))
        day_record = UnifiedReport(day, water_register)
        ret.append(day_record)
        
    return  ret


"""

Object used for display by the template. Each object is for one
calendar date. It contains the date and the water register for this day, in
addition to a list of probe readings (uga_records) and a list of forms, each
corresponding to one manual water event. The forms are extracted from the formset

"""


class UnifiedReport:
    
    def __init__(self, date, water_register):
        self.date = date
        self.water_register = water_register
        self.uga_records = []
        self.forms = []
