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

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + datetime.timedelta(days=n)

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
    message = cse.crop_event.irrigation_message
    irrigate_to_max = cse.crop_event.irrigate_to_max
    return (stage, dwu, message, irrigate_to_max)


def date_of_last_rainfall_or_irrigation(field, current_date):
    pass


def max_temp_since_last_rainfall_or_irrigation(field, current_date):
    pass


def quantize( f ):
    """ Convert to a Decimal with resolution of 0.01 """
    # An issue within the python Decimal class causes conversion from
    # Decimal to Decimal to fail if the module is reloaded.  Work
    # around that issue by converting to string, then to a Decimal.
    retval = Decimal(str(f)).quantize( Decimal('0.01') )

    return retval

OPTIMIZE=True

def generate_water_register(crop_season, field, user):

    ## Determine the first event date (planting) to show
    planting_event = CropSeasonEvent.objects.filter(crop_season=crop_season,
                                                    field=field,
                                                    crop_event__name='Planting').order_by("-date").first()

    if not planting_event: return (None, None)


    ## First and last event date (end of season) to show
    start_date = planting_event.date
    end_date   = crop_season.season_end_date + datetime.timedelta(1)

    if OPTIMIZE:
        ## Cache database query ##
        wr_query = WaterRegister.objects.filter(crop_season=crop_season,
                                                field=field, 
                                                date__gte=start_date,
                                                date__lte=end_date)
        

    maxWater = float(field.soil_type.max_available_water)

    ## Assume that each field starts with a full water profile
    AWC_initial = maxWater


    ## First pass, calculate water profile (AWC)
    AWC_prev = AWC_initial
    for  date in daterange(start_date, end_date):
        ## Get or Create a water register object (db record)
        try: 
            if OPTIMIZE:
                wr = wr_query.filter(date=date)[0]
            else:
                wr = WaterRegister.objects.get(crop_season=crop_season,
                                               field=field, 
                                               date=date)
        except:
            wr = WaterRegister(
                crop_season = crop_season,
                field = field,
                date = date
            )

        ( wr.crop_stage, 
          wr.daily_water_use, 
          wr.message, 
          wr.irrigate_to_max ) = get_stage_and_daily_water_use(field, date)

        AWC_probe = calculateAWC_ProbeReading(crop_season, field, date)
        wr.rain, wr.irrigation  = caclulateAWC_RainIrrigation(crop_season, field, date)

        if AWC_probe is None: 
            wr.average_water_content = float(AWC_prev) - float(wr.daily_water_use) + float(wr.rain) + float(wr.irrigation)
        else:
            wr.average_water_content = float(AWC_probe)

        if wr.average_water_content > maxWater: 
            wr.average_water_content = maxWater
        AWC_prev = wr.average_water_content

        from django.contrib.auth.models import User
        user = User.objects.get(pk=1)
        wr.muser_id = user.pk
        wr.cuser_id = user.pk

        wr.save()


    if OPTIMIZE:
        ## Refresh query
        wr_query = WaterRegister.objects.filter(crop_season=crop_season,
                                                field=field, 
                                                date__gte=start_date,
                                                date__lte=end_date)
        
    ## Second pass, calculate flags 
    irrigate_to_max_flag_seen = False
    irrigate_to_max_achieved  = False
    drydown_flag              = False
    irrigate_to_max_days      = 0
    for date in daterange(start_date, end_date):

        if OPTIMIZE:
            wr = wr_query.filter(date=date)[0]
        else:
            wr = WaterRegister.objects.get(crop_season=crop_season,
                                           field=field, 
                                           date=date)

        date_plus5 = date + datetime.timedelta(days=5)
        try:
            wr_plus5 = WaterRegister.objects.get(crop_season=crop_season, 
                                                 field=field, 
                                                 date=date_plus5)
        except:
            wr_plus5 = None

        if wr.irrigate_to_max: 
            irrigate_to_max_flag_seen = True

        #####
        ## If the irrigate_to_max flag has been seen, irrigate & check
        ## sensors until maxWater is achieved (or 3 watering days have
        ## occured), then no more irrigation and no more sensor checks   
        ## ('drydown') 
        #####
        if not irrigate_to_max_flag_seen:
            wr.irrigate_flag        = wr.average_water_content       < 0.00

            if wr_plus5.average_water_content:
                wr.check_sensors_flag = wr_plus5.average_water_content < 0.00

        else:
            if irrigate_to_max_achieved or irrigate_to_max_days >= 3:
                wr.irrigate_flag = False
                wr.dry_down_flag = True
            else:
                irrigate_to_max_days += 1
                if wr.average_water_content >= maxWater:
                    irrigate_to_max_achieved = True
                    wr.irrigate_flag         = False
                    wr.check_sensors_flag    = False
                    wr.dry_down_flag         = True
                else:
                    wr.irrigate_flag      = True
                    wr.check_sensors_flag = True

        wr.save()

    return
