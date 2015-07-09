from django.db.models import DateField
from django.utils import timezone
from django.db.models import Q
from django.core.urlresolvers import reverse, reverse_lazy

from farms.models import Farm, CropSeason, Field, WaterRegister, WaterHistory, Farm, CropSeasonEvent, Probe, ProbeReading
from datetime import date, datetime

from farms.generate_water_register import generate_water_register

# workarounds for the absence of query datetime__date operator
from common.utils import d2dt_min, d2dt_max, d2dt_range


def farms_filter(user):
    return Farm.objects.filter( Q(farmer=user) |
                                Q(users=user) ).distinct()


# Could probably use lamdba...
def cumulative_water(wr_list):
    total_rain = 0
    total_irr = 0
    water_use = 0
    days_of_irrigation = 0
    for wr in wr_list:
        total_rain += wr.rain
        total_irr += wr.irrigation
        water_use += wr.daily_water_use
        if (wr.irrigation > 0):
            days_of_irrigation += 1
        
    return (total_rain, total_irr, water_use, days_of_irrigation)


def generate_cumulative_report(start_date, end_date, user):

    ret_list = []
    farm_list = farms_filter(user)
    crop_season_list = CropSeason.objects.filter(season_start_date__lte = end_date,
                                                 season_end_date__gte = start_date).all()

    # Now a field can be associated to more than one crop season

    # Create a dictionary with ('field', 'crop_season')
    all_fields = {}
    for cs in crop_season_list:
        for field in cs.field_list.all():
            if field.farm not in farm_list: continue
            cumulative_report = get_cumulative_report(field.farm, field, cs, user, start_date, end_date)
            if cumulative_report is not None:
                ret_list.append(cumulative_report)
    
    return ret_list



def get_cumulative_report(farm, field, crop_season, user, start_date, end_date):

    generate_water_register(crop_season,
                            field,
                            user,
                            None,
                            end_date)

                
    # Will add an entry for this field and farm
            
    crf = CumulativeReportFields()
    crf.field = field
    crf.farm = farm
    crf.crop = crop_season.crop
    crf.start_date = crop_season.season_start_date
    crf.end_date = crop_season.season_end_date

    # Get the water registry for the crop season / field
    wr_list = WaterRegister.objects.filter(crop_season = crop_season, 
                                           field = field).order_by('-datetime').filter(Q(datetime__gte = d2dt_min(start_date), \
                                                                                         datetime__lte = d2dt_max(end_date)
                                                                                         )
                                                                                       )
                                                                                         
                
    if len(wr_list) == 0: return None
    wr = wr_list[0]
    if (wr is not None):
        (crf.cumulative_rain, 
         crf.cumulative_irrigation_vol, 
         crf.cumulative_water_use,
         crf.days_of_irrigation) = cumulative_water(wr_list)
         
        # Add link to water register
        crf.water_register_url = reverse('water_register_season_field_date',
                                          kwargs={'season':crop_season.pk,
                                                  'field':field.pk,
						  'date':end_date }
                                          )

    return crf




###
### Create a cumulative report for one user, indexed be field pk,
### for the given report date.
###


def cumulative_report_by_field(start_date, end_date, user):
    reports = generate_cumulative_report(report_date, user)
    ret = {};
    for report in reports:
        ret[report.field.pk] = report
    return ret



class CumulativeReportFields:

    # Provide default values for all the fields
    farm                        = 'Unknown farm'
    field                       = 'Unknown field'
    crop                        = 'Unknown crop'
    start_date                  = 'No Entry'
    end_date                    = 'No Entry'
    link_to_water_reg           = ''
    cumulative_rain             = 0.0
    cumulative_irrigation_vol   = 0.0
    cumulative_water_use        = 0
    days_of_irrigation          = 0

