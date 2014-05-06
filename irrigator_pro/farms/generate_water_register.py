import datetime
import os, os.path
import math
import sys
import time
from decimal import Decimal

from irrigator_pro.settings import ABSOLUTE_PROJECT_ROOT
from farms.models import *
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

def calculateAWC_ProbeReading(crop_season, field, date):
    """
    Calculate the Available Water Content for the specified field and
    date from Probe Reading data (if available).  If no probe reading
    exists, returns None.
    """

    ## Find the probe/radio_id for this field (if any)
    try:
        probe = Probe.objects.get(crop_season=crop_season, field_list=field)
    except ObjectDoesNotExist:
        return None

    radio_id = probe.radio_id

    # ## Determine the crop that corresponds to this date
    # crop_season = CropSeason.objects.filter(field_list=field,
    #                                         season_start_date__lte=date,
    #                                         season_end_date__gte=date,
    #                                         )
    # if( crop_season.count() > 1 ):
    #     raise RuntimeError("More than one crop season for field '%s' on %s." % (field, date))
    # crop_season = crop_season.first()

    ## Get the maximum root depth
    if crop_season:
        crop = crop_season.crop
        max_root_depth = crop_season.crop.max_root_depth
    else:
        return None

    ## Find any probe readings for date with this radio_id
    probe_reading = ProbeReading.objects.filter(radio_id=radio_id,
                                                reading_datetime__startswith=date)

    ## Get the most recent one for this date
    probe_reading = probe_reading.order_by('reading_datetime').last()
    if not probe_reading:
        return None

    ## Extract soil parameters
    soil_type_parameters = SoilTypeParameter.objects.filter(soil_type=field.soil_type)

    try:
        soil_type_8in  = soil_type_parameters.get(depth=8 )
    except ObjectDoesNotExist:
        raise RuntimeError("Missing parameters for soiltype '%s': %d inch depth missing" % ( field.soil_type, 8) )

    try:
        soil_type_16in = soil_type_parameters.get(depth=16)
    except ObjectDoesNotExist:
        raise RuntimeError("Missing parameters for soiltype '%s': %d inch depth missing" % ( field.soil_type, 16) )

    try:
        soil_type_24in = soil_type_parameters.get(depth=24)
    except ObjectDoesNotExist:
        raise RuntimeError("Missing parameters for soiltype '%s': %d inch depth missing" % ( field.soil_type, 24) )

    #####
    ## Calculate available water content (AWC) at each depth
    #####
    ##
    ## The AWC is the difference between the total water in a block of
    ## soil 24" tall at the sensor reading and the total water in that
    ## same block of soil at a sensor reading of 40 kPa.  40 kPa is
    ## considered to be the "threshold" value at which the plant can
    ## no longer extract water efficiently.
    ##
    ## The total water is calculated at the sensor reading:
    ##    TWC(probe) = [b0 + b1*ln(probe)]*24
    ##
    ## The total water at our threshold value is also calculated:
    ##    TWC(40) = [b0 + b1*ln(40)]*24
    ##
    ## The difference between the two is the Available Water Content:
    ##    AWC      = TWC(probe) - TWC(40)
    ##             = {[b0 + b1*ln(probe)]*24 - [b0 + b1*ln(40)]*24}
    ##             = 24*{[b0 +b1*ln(probe)] - [b0 + b1*ln(40)]}
    ##             = 24 * {b0 - b0 + b1*ln(probe) - b1*ln(40)}
    ##             = 24 *{b1*ln(probe) - b1*ln(40)}
    ##             = 24 * b1 * [ln(probe) - ln(40)]
    ##
    ##

    def safelog( val ):
        if val <= 0:
            return float("-inf")
        else:
            return math.log( float(val) )

    ln40 = math.log(40.0)

    AWC_8  = soil_type_8in.slope  * ( safelog(probe_reading.soil_potential_8)  - ln40 ) * 24
    AWC_16 = soil_type_16in.slope * ( safelog(probe_reading.soil_potential_16) - ln40 ) * 24
    AWC_24 = soil_type_24in.slope * ( safelog(probe_reading.soil_potential_24) - ln40 ) * 24

    if AWC_8  > field.soil_type.max_available_water: AWC_8  = float(field.soil_type.max_available_water)
    if AWC_16 > field.soil_type.max_available_water: AWC_16 = float(field.soil_type.max_available_water)
    if AWC_24 > field.soil_type.max_available_water: AWC_24 = float(field.soil_type.max_available_water)

    #####
    ## Calculate average AWC at the depths accessible to the crop
    ## roots.
    #####
    ## NB: This would probably be better done via a linear
    ##     interpolation, rather than discrete steps.
    if max_root_depth <= 8:
        AWC = AWC_8
    elif max_root_depth <= 16:
        AWC = (AWC_8 + AWC_16) / 2
    else: # max_root_depth > 16
        AWC = (AWC_8 + AWC_16 + AWC_24)/3

    return AWC


def caclulateAWC_RainIrrigation(season, field, date):

    wh = WaterHistory.objects.filter(crop_season=season,
                                     field_list=field,
                                     date=date
                                    ).last()

    if wh:
        return ( wh.rain, wh.irrigation )
    else:
        return ( 0.0, 0.0 )


def get_stage_and_daily_water_use(field, date):
    cse = CropSeasonEvent.objects.filter(crop_season__field_list=field,
                                         date__lte=date).distinct().order_by('-date').first()
    dwu = cse.crop_event.daily_water_use
    stage = cse.crop_event.name
    description = cse.crop_event.description
    irrigate_to_max = cse.crop_event.irrigate_to_max
    return (stage, dwu, description, irrigate_to_max)


def date_of_last_rainfall_or_irrigation(field, current_date):
    pass


def max_temp_since_last_rainfall_or_irrigation(field, current_date):
    pass


def need_irrigation(AWC):
    return AWC < 0.00


def check_sensors(AWC):
    return AWC < 0.30


def quantize( f ):
    """ Convert to a Decimal with resolution of 0.01 """
    # An issue within the python Decimal class causes conversion from
    # Decimal to Decimal to fail if the module is reloaded.  Work
    # around that issue by converting to string, then to a Decimal.
    retval = Decimal(str(f)).quantize( Decimal('0.01') )

    return retval


def generate_water_register(crop_season, field):

    ## Determine the first event date (planting) to show
    planting_event = CropSeasonEvent.objects.filter(crop_season=crop_season,
                                                    field=field,
                                                    crop_event__name='Planting').order_by("-date").first()

    if not planting_event: return (None, None)

    start_date = planting_event.date

    ## Determine the last event date (end of season) to show
    end_date = crop_season.season_end_date

    maxWater = float(field.soil_type.max_available_water)

    AWC_initial = maxWater

    table_header = ( 'Crop Season',
                     'Field',
                     'Date',
                     'Growth Stage',
                     'DWU',
                     'Rain',
                     'Irrigation',
                     'AWC',
                     'From Probes',
                     'Irrigate',
                     'Check Sensors',
                     'Dry Down',
                     'Description')
    table_rows = []

    date = start_date
    AWC_prev = AWC_initial
    irrigate_to_max_flag_seen = False
    irrigate_to_max_achieved  = False
    drydown_flag              = False 
    while date <= end_date:

        (stage, DWU, description, irrigate_to_max) = get_stage_and_daily_water_use(field, date)

        if irrigate_to_max: irrigate_to_max_flag_seen = True

        AWC_probe = calculateAWC_ProbeReading(crop_season, field, date)
        rain, irrigation  = caclulateAWC_RainIrrigation(crop_season, field, date)

        if AWC_probe is None: 
            AWC = float(AWC_prev) - float(DWU) + float(rain) + float(irrigation)
        else:
            AWC = AWC_probe

        if AWC > maxWater: AWC = maxWater

        #####
        ## If the irrigate_to_max flag has been seen, irrigate & check sensors until 
        ## maxWater is achieved, then no more irrigation and no more sensor checks
        ## ('drydown') 
        #####
        if not irrigate_to_max_flag_seen:
            need_irrigation_flag = need_irrigation(AWC)
            check_sensors_flag   = check_sensors(AWC)
        else:
            if irrigate_to_max_achieved:
                need_irrigation_flag = False
                check_sensors_flag = False
            else:
                if AWC >= maxWater:
                    irrigate_to_max_achieved = True
                    need_irrigation_flag     = False
                    check_sensors_flag       = False
                    drydown_flag             = True
                else:
                    need_irrigation_flag = True
                    check_sensors_flag = True


        row = ( crop_season,
                field,
                date,
                stage,
                quantize(DWU),
                quantize(rain),
                quantize(irrigation),
                quantize(AWC),

                (not AWC_probe is None),
                need_irrigation_flag,
                check_sensors_flag,
                drydown_flag,
                description,
                )

        table_rows.append( row )  

        AWC_prev = AWC
        date += datetime.timedelta(days=1)

    return ( table_header, table_rows )
