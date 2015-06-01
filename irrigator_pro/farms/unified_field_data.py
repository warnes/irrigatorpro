from farms.models import *
from common.utils import daterange

from farms.generate_water_register import generate_water_register
from farms.utils import get_probe_readings
from django.db.models import Q

def generate_objects(crop_season, field, user,  report_date):
    
    if crop_season.season_start_date > report_date:
        print "Report date earlier than start of season"
        return None
    
    if crop_season.season_end_date < report_date:
        print "bringing report date back to end of season date"
        report_date = crop_season.season_end_date

    generate_water_register(crop_season, field, user, report_date)
    water_register_query = WaterRegister.objects.filter(crop_season = crop_season,
                                                        field = field).order_by('-date').filter(Q(date__lte =  report_date))
    
    ### probe_readings will contain all the readings in increasing order of time.
    probe_readings = get_probe_readings(crop_season, field, None, report_date).reverse()
    
    
    water_history_query = WaterHistory.objects.filter(crop_season=crop_season,
                                                          field_list=field).all()
    
    ##
    
    ret = []
    current_probe_reading = None
    if probe_readings is not None and len(probe_readings) > 0:
        current_probe_reading = probe_readings.pop()
        while current_probe_reading is not None and current_probe_reading.reading_datetime.date() < crop_season.season_start_date:
            if len(probe_readings) == 0:
                current_probe_reading = None
            else:
                current_probe_reading = probe_readings.pop()

                
        
        
        
    for day in daterange(crop_season.season_start_date, report_date):
        try:
            water_register = water_register_query.get(date = day)
            day_record = UnifiedReport(day, water_register)
            for wh in water_history_query.filter(date=day):
                day_record.manual_records.append(wh)
            while current_probe_reading is not None and current_probe_reading.reading_datetime.date() == day:
                day_record.manual_records.append(current_probe_reading)
                current_probe_reading = probe_readings.pop()
            
            ret.append(day_record)
            
        except BaseException as x:
            print 'BaseException caught, but should not be an error here!!!'
            print "Exception message: ", x
            return None
        
    return ret

    
    
    
    
class UnifiedReport:
    
    def __init__(self, date, water_register):
        self.date = date
        self.water_register = water_register
        self.uga_records = []
        self.manual_records = []
    
    