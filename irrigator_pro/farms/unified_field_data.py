from farms.models import *
from common.utils import daterange

from farms.generate_water_register import generate_water_register
from farms.utils import get_probe_readings
from django.forms.models import modelformset_factory

from django.db.models import Q





def get_wh_formset(crop_season, field):
    print "Getting wh formset"
    water_history_query = WaterHistory.objects.filter(crop_season=crop_season,
                                                          field_list=field).all().order_by("date")
    WaterHistoryFormSet = modelformset_factory(WaterHistory, fields = [
        'date',
        'soil_potential_8',
        'soil_potential_16',
        'soil_potential_24',
        'min_temp_24_hours',
        'max_temp_24_hours',
        'ignore',
        'rain',
        'irrigation'
    ])

    formset = WaterHistoryFormSet(queryset = water_history_query)
    return formset




def generate_objects(crop_season, field, user,  report_date):
    
    if crop_season.season_start_date > report_date:
        print "Report date earlier than start of season"
        return None
    
    if crop_season.season_end_date < report_date:
        print "bringing report date back to end of season date"
        report_date = crop_season.season_end_date

    print "Generating water register"
    generate_water_register(crop_season, field, user, report_date)
    water_register_query = WaterRegister.objects.filter(crop_season = crop_season,
                                                        field = field).order_by('-date').filter(Q(date__lte =  report_date))
    
    ### probe_readings will contain all the readings in increasing order of time.
    print "Getting probe readings"
    probe_readings = get_probe_readings(crop_season, field, None, report_date)
    probe_readings.reverse()

    print "Getting formset"
    wh_formset = get_wh_formset(crop_season, field)
    
    
    ##
    
    print "Creating return objects."
    ret = []
    current_probe_reading = None
    if probe_readings is not None and len(probe_readings) > 0:
        current_probe_reading = probe_readings.pop()
        while current_probe_reading is not None and current_probe_reading.reading_datetime.date() < crop_season.season_start_date:
            if len(probe_readings) == 0:
                current_probe_reading = None
            else:
                current_probe_reading = probe_readings.pop()

    print "Initalizinng"
    form_index = 0
    current_form = None
    all_forms = wh_formset.forms
    if all_forms is not None and len(all_forms) > 0:
        current_form = all_forms[form_index]
        form_index = form_index + 1
        while current_form is not None and current_form['date'].value() < crop_season.season_start_date:
            if form_index == len(forms):
                current_form = None
            else:
                current_form = forms[form_index]
                form_index = form_index + 1
                

    print "Actually creating"
        
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
            print 'BaseException caught, but should not be an error here!!!'
            print "Exception message: ", x
            return None
        
    print "Returning"
    return (wh_formset, ret)

    
    
    
    
class UnifiedReport:
    
    def __init__(self, date, water_register):
        self.date = date
        self.water_register = water_register
        self.uga_records = []
        self.forms = []
