import datetime
import os, os.path
import math
import sys
import time
from decimal import Decimal

from irrigator_pro.settings import ABSOLUTE_PROJECT_ROOT, COMPUTE_FULL_SEASON
from farms.models import *
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + datetime.timedelta(days=n)

def calculateAWC_ProbeReading(crop_season, field, date, 
                              probe=None, 
                              probe_reading_query=None, 
                              soil_type_parameter_query=None):
    """
    Calculate the Available Water Content for the specified field and
    date from Probe Reading data (if available).  If no probe reading
    exists, returns None.
    """

    ## Find the probe/radio_id for this field (if any)
    if probe is None:
        try:
            probe = Probe.objects.get(crop_season=crop_season, field_list=field)
        except ObjectDoesNotExist:
            return None

    radio_id = probe.radio_id

    ## Get the maximum root depth
    if crop_season:
        crop = crop_season.crop
        max_root_depth = crop_season.crop.max_root_depth
    else:
        return None

    if probe_reading_query is None:
        probe_reading_query = ProbeReading.objects.filter(radio_id=radio_id).all()

        
    ## Find any probe readings for date with this radio_id
    probe_reading = probe_reading_query.filter(reading_datetime__startswith=date)

    ## Filter down to the the most recent one for this date
    probe_reading = probe_reading.order_by('reading_datetime').last()
    if not probe_reading:
        return None

    ## Extract soil parameters
    if soil_type_parameter_query is None:
        soil_type_parameter_query = SoilTypeParameter.objects.filter(soil_type=field.soil_type).all()

    try:
        soil_type_8in  = soil_type_parameter_query.get(depth=8 )
    except ObjectDoesNotExist:
        raise RuntimeError("Missing parameters for soiltype '%s': %d inch depth missing" % ( field.soil_type, 8) )

    try:
        soil_type_16in = soil_type_parameter_query.get(depth=16)
    except ObjectDoesNotExist:
        raise RuntimeError("Missing parameters for soiltype '%s': %d inch depth missing" % ( field.soil_type, 16) )

    try:
        soil_type_24in = soil_type_parameter_query.get(depth=24)
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


def calculateAWC_RainIrrigation(crop_season, field, date, water_history_query=None):

    if water_history_query is None:
        water_history_query = WaterHistory.objects.filter(crop_season=crop_season,
                                                          field_list=field).all()

    wh = WaterHistory.objects.filter(date=date).last()

    if wh:
        return ( wh.rain, wh.irrigation )
    else:
        return ( 0.0, 0.0 )


def get_stage_and_daily_water_use(field, date, crop_season_events_query=None):
    
    if crop_season_events_query is None:
        crop_season_events_query = CropSeasonEvent.objects.filter(crop_season__field_list=field).distinct().all()

    cse = crop_season_events_query.filter(date__lte=date).distinct().order_by('-date').first()

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

    ## Cache values / queries for later use
    probe = Probe.objects.get(crop_season=crop_season, field_list=field)
    radio_id = probe.radio_id
    probe_reading_query       = ProbeReading.objects.filter(radio_id=radio_id).all()
    soil_type_parameter_query = SoilTypeParameter.objects.filter(soil_type=field.soil_type).all()
    water_history_query       = WaterHistory.objects.filter(crop_season=crop_season,
                                                            field_list=field).all()
    crop_season_events_query = CropSeasonEvent.objects.filter(crop_season__field_list=field).distinct().all()

    ## First and last event date (end of season) to show
    start_date = planting_event.date
    season_end_date   = crop_season.season_end_date + datetime.timedelta(1)

    today = datetime.date.today()
    today_plus5 = today + datetime.timedelta(days=5)

    if COMPUTE_FULL_SEASON:
        end_date = season_end_date
    else:
        end_date = min(today_plus5, season_end_date)

    wr_query = WaterRegister.objects.filter(crop_season=crop_season,
                                            field=field, 
                                            date__gte=start_date,
                                            date__lte=end_date).all()

    maxWater = float(field.soil_type.max_available_water)

    ## Assume that each field starts with a full water profile
    AWC_initial = maxWater


    ## First pass, calculate water profile (AWC)
    AWC_prev = AWC_initial
    for  date in daterange(start_date, end_date):
        ## Get or Create a water register object (db record)
        try: 
            wr = wr_query.filter(date=date)[0]
        except ( ObjectDoesNotExist,  IndexError, ):
            wr = WaterRegister(
                crop_season = crop_season,
                field = field,
                date = date
            )

        ( wr.crop_stage, 
          wr.daily_water_use, 
          wr.message, 
          wr.irrigate_to_max ) = get_stage_and_daily_water_use(field, date, 
                                                               crop_season_events_query=crop_season_events_query)

        AWC_probe = calculateAWC_ProbeReading(crop_season, field, date, 
                                              probe=probe, 
                                              probe_reading_query=probe_reading_query, 
                                              soil_type_parameter_query=soil_type_parameter_query)

        wr.rain, wr.irrigation  = calculateAWC_RainIrrigation(crop_season, field, date, 
                                                              water_history_query=water_history_query)

        if AWC_probe is None: 
            wr.average_water_content = float(AWC_prev) - float(wr.daily_water_use) + float(wr.rain) + float(wr.irrigation)
            wr.computed_from_probes  = False
        else:
            wr.average_water_content = float(AWC_probe)
            wr.computed_from_probes  = True

        if wr.average_water_content > maxWater: 
            wr.average_water_content = maxWater
        AWC_prev = wr.average_water_content

        from django.contrib.auth.models import User
        user = User.objects.get(pk=1)
        wr.muser_id = user.pk
        wr.cuser_id = user.pk

        wr.save()


    ## Refresh query
    wr_query = WaterRegister.objects.filter(crop_season=crop_season,
                                            field=field, 
                                            date__gte=start_date,
                                            date__lte=end_date).all()
        
    ## Second pass, calculate flags 
    irrigate_to_max_flag_seen = False
    irrigate_to_max_achieved  = False
    drydown_flag              = False
    irrigate_to_max_days      = 0
    for date in daterange(start_date, end_date):

        wr = wr_query.filter(date=date)[0]

        if wr.irrigate_to_max: 
            irrigate_to_max_flag_seen = True

        #####
        ## If the irrigate_to_max flag has been seen, irrigate & check
        ## sensors until maxWater is achieved (or 3 watering days have
        ## occured), then no more irrigation and no more sensor checks   
        ## ('drydown') 
        #####
        if not irrigate_to_max_flag_seen:
            ##
            # Check if wee need to irrigate *today*
            wr.irrigate_flag = wr.average_water_content < 0.00
            ##

            ##
            # Check if we need to irrigate in the next five days
            ##
            wr.check_sensors_flag = False

            date_plus5 = date + datetime.timedelta(days=5)
            for date_future in daterange(date, date_plus5):
                try:
                    wr_future = wr_query.get(date=date_future)
                    wr.check_sensors_flag = wr.check_sensors_flag or (wr_future.average_water_content < 0.00)
                except ObjectDoesNotExist:
                    pass

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
