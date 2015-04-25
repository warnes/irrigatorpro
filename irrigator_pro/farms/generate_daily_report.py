from django.db.models import DateField
from django.utils import timezone
from django.db.models import Q
from django.core.urlresolvers import reverse, reverse_lazy

from farms.models import Farm, CropSeason, Field, WaterRegister, WaterHistory, Farm, CropSeasonEvent, Probe, ProbeReading
from datetime import date, datetime

from farms.generate_water_register import generate_water_register

def farms_filter(user):
    return Farm.objects.filter( Q(farmer=user) |
                                Q(users=user) ).distinct()


# Could probably use lamdba...
def cumulative_water(wr_list):
    total_rain = 0
    total_irr = 0
    for wr in wr_list:
        total_rain += wr.rain
        total_irr += wr.irrigation

    return (total_rain, total_irr)


def generate_daily_report(report_date, user):

    ret_list = []
    farm_list = farms_filter(user)
    crop_season_list = CropSeason.objects.filter(season_start_date__lt = report_date,
                                                 season_end_date__gte = report_date).all()

    # Create a dictionary with ('field', 'crop_season')
    crop_season_field = {}
    for x in crop_season_list:
        for field in x.field_list.all():
            crop_season_field[field] = x
    
    for farm in farm_list:

        field_list = Field.objects.filter(farm = farm)
        for field in field_list:

            # Get all the crop_season objects that:
            #    - field_list contains the field

            if field not in crop_season_field: continue
            else: 
                daily_report = get_daily_report(farm, field, crop_season_field[field], user, report_date)
                if daily_report is not None:
                    ret_list.append(daily_report)
    
    return ret_list


def get_daily_report(farm, field, crop_season, user, report_date):

    generate_water_register(crop_season,
                            field,
                            user,
                            None,
                            report_date)

    # Will add an entry for this field and farm
            
    srf = SummaryReportFields()
    srf.field = field
    srf.farm = farm
    srf.crop = crop_season.crop
    srf.water_register_url = reverse('water_register_season_field_date', 
                                     kwargs={'season': crop_season.pk,
                                             'field':  field.pk,
                                             'date':   report_date}
                                     )

    # Get the water registry for the crop season / field

    wr_list = WaterRegister.objects.filter(crop_season = crop_season, 
                                           field = field).order_by('-date').filter(Q(date__lte =  report_date))

    if len(wr_list) == 0: return None
    wr = wr_list[0]
    if (wr is not None):
        srf.growth_stage    = wr.crop_stage
        srf.message         = wr.message
        (srf.cumulative_rain, srf.cumulative_irrigation_vol) = cumulative_water(wr_list)
        srf.days_to_irrigation = wr.days_to_irrigation

        # Get the last event for the field. It will be either rain, irrigation,
        # manual reading or automated reading.
        
        # First get the latest water event from water history
        # The water history contains a field list (although right now it
        # may be limited to one field.) Still, assume there could be more
        # than one.

        whList = WaterHistory.objects.filter(crop_season = crop_season)
        # Just keep the ones with one of the fields equal to current field.
                    
        latest_water_record = None
        if len(whList) > 0:
            latestWH = whList.filter(field_list = field) #.latest('date')
            latest_water_record = whList.latest('date')

            # Now get the latest measurement record from the probes.
            # First all the probes for a given pair (field, crop season)

            probe_list = Probe.objects.filter(field_list = field, crop_season = crop_season)
            latest_probe_reading = None
            if (len(probe_list) > 0):
                radio_id = probe_list[0].radio_id
                probe_readings = ProbeReading.objects.filter(radio_id = radio_id)
                # Same radio id can be used across seasons. Filter based on (Start, end) of 
                # crop season
                probe_readings = probe_readings.filter(reading_datetime__gte = crop_season.season_start_date,
                                                       reading_datetime__lte = crop_season.season_end_date)
                if (probe_readings is not None):
                    latest_probe_reading = probe_readings.latest('reading_datetime')
                    
                        

            # Compare both records, keep most recent.
            # Probably easier way in python to do this. Can worry later.
            latest_is_wr = None
            if (latest_water_record is None and latest_probe_reading is None): pass
            elif  (latest_water_record is not None and latest_probe_reading is not None):
                latest_is_wr = True if (latest_water_record.date > latest_probe_reading.reading_datetime.date()) else False
            else:
                if (latest_water_record is not None):
                    latest_is_wr = True
                else:
                    latest_is_wr = False
            if (latest_is_wr is not None):
                if (latest_is_wr):
                    srf.last_data_entry_type = "Rain or irrigation"
                    # Ensure we have a datetime object for consistency in data
                    x = latest_water_record.date
                    srf.time_last_data_entry = datetime(x.year, x.month, x.day)
                else:
                    srf.last_data_entry_type = "Probe reading"
                    srf.time_last_data_entry = latest_probe_reading.reading_datetime
            
                    # Add link to water register
            
            # Add the water register object to get next irrigation date, or status.
            # Only add if planting season is not over.
            if (crop_season.season_end_date >= report_date):
                srf.water_register_object = wr

    return srf


###
### Create a daily report for one user, indexed be field pk,
### for the given report date.
###


def daily_report_by_field(report_date, user):
    reports = generate_daily_report(report_date, user)
    ret = {};
    for report in reports:
        ret[report.field.pk] = report
    return ret


class SummaryReportFields:

    # Provide default values for all the fields
    farm                        = 'Unknown farm'
    field                       = 'Unknown field'
    crop                        = 'Unknown crop'
    growth_stage                = 'Undetermined stage'
    last_data_entry_type        = 'No Entry'
    time_last_data_entry        = 'No Entry' #DateField(default=timezone.now())
    cumulative_rain             = 0.0
    cumulative_irrigation_vol   = 0.0
    days_to_irrigation          = 0
    water_register_url          = ''
    water_register_object       = None
    message                     = 'something'
