from farms.models import *
from common.utils import daterange

from farms.generate_water_register import generate_water_register
from farms.utils import get_probe_readings
from django.forms.models import modelformset_factory

from django.db.models import Q

from datetime import datetime, date

###
### Sometimes the is a string, sometime a string.
### always convert to date

def getDateObject(thisDate):
    if isinstance(thisDate, date):
        return thisDate
    return datetime.strptime(thisDate, "%Y-%m-%d").date()

def generate_objects(wh_formset, crop_season, field, user,  report_date):

    if crop_season.season_start_date > report_date:
        return None
    
    if crop_season.season_end_date < report_date:
        report_date = crop_season.season_end_date

    generate_water_register(crop_season, field, user, report_date)
    water_register_query = WaterRegister.objects.filter(crop_season = crop_season,
                                                        field = field).order_by('-date').filter(Q(date__lte =  report_date))
    
    ### probe_readings will contain all the readings in increasing order of time.
    probe_readings = get_probe_readings(crop_season, field, None, report_date)
    probe_readings.reverse()

    ret = []
    current_probe_reading = None
    if probe_readings is not None and len(probe_readings) > 0:
        current_probe_reading = probe_readings.pop()
        while current_probe_reading is not None and current_probe_reading.reading_datetime.date() < crop_season.season_start_date:
            if len(probe_readings) == 0:
                current_probe_reading = None
            else:
                current_probe_reading = probe_readings.pop()

    form_index = 0
    current_form = None
    all_forms = wh_formset.forms
    if all_forms is not None and len(all_forms) > 0:
        current_form = all_forms[form_index]
        form_index = form_index + 1

        while current_form is not None and getDateObject(current_form['date'].value()) < crop_season.season_start_date:
            if form_index == len(forms):
                current_form = None
            else:
                current_form = forms[form_index]
                form_index = form_index + 1
                

    for day in daterange(crop_season.season_start_date, report_date):
        try:
            water_register = water_register_query.get(date = day)
            day_record = UnifiedReport(day, water_register)

            ## Next two while
            while current_probe_reading is not None and current_probe_reading.reading_datetime.date() == day:
                day_record.uga_records.append(current_probe_reading)
                if len(probe_readings) > 0:
                    current_probe_reading = probe_readings.pop()
                else:
                    current_probe_reading = None


            while current_form is not None and current_form['date'].value() == day:
                day_record.forms.append(current_form)
                if form_index == len(all_forms):
                    current_form = None
                else:
                    current_form = all_forms[form_index]
                    form_index = form_index + 1

            ret.append(day_record)
            
        except BaseException as x:
            return None
        
    return  ret


    
class UnifiedReport:
    
    def __init__(self, date, water_register):
        self.date = date
        self.water_register = water_register
        self.uga_records = []
        self.forms = []
