from datetime import timedelta
import os, os.path
import math
import sys
import time
from decimal import Decimal
from numpy import nanmean

from irrigator_pro.settings import ABSOLUTE_PROJECT_ROOT, COMPUTE_FULL_SEASON
from farms.models import *
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(days=n)

def calculateAWC_ProbeReading(crop_season, field, date, 
                              probe=None, 
                              probe_reading_query=None, 
                              soil_type_parameter_query=None):
    """
    Calculate the Available Water Content for the specified field and date
    from Probe Reading data (if available).  If no probe reading
    exists, returns None.

    Also returns the temperature, so that the return value is a tuple
    of (AWC, temp)
    """

    ## Find the probe/radio_id for this field (if any)
    if probe is None:
        try:
            probe = Probe.objects.get(crop_season=crop_season, field_list=field)
        except ObjectDoesNotExist:
            return ( None, None )

    radio_id = probe.radio_id

    ## Get the maximum root depth
    if crop_season:
        crop = crop_season.crop
        max_root_depth = crop_season.crop.max_root_depth
    else:
        return ( None, None )

    if probe_reading_query is None:
        probe_reading_query = ProbeReading.objects.filter(radio_id=radio_id).all()

        
    ## Find any probe readings for date with this radio_id
    probe_reading = probe_reading_query.filter(reading_datetime__startswith=date)

    ## Filter down to the the most recent one for this date
    probe_reading = probe_reading.order_by('reading_datetime').last()
    if not probe_reading:
        return ( None, None )

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


    ####
    ## Extract temperature 
    ####
    temp1 = celciusToFarenheit( probe_reading.thermocouple_1_temp )
    temp2 = celciusToFarenheit( probe_reading.thermocouple_2_temp )
    
    ### Current probes don't actually have two temperature probes
    ### installed.  Only the first probe is installed and operational,
    ### so ignore the second and simply use the first one.
    ## temp = twoTempAverage(temp1, temp2)
    temp = tempRangeCheck(temp1)

    return (AWC, temp)


def celciusToFarenheit(celcius):
    if celcius is None:
        return None
    else:
        return float(celcius) * 1.8 + 32.0 


def tempRangeCheck(temp):
    """
    Apply temperature sanity check (assuming temp in degrees
    Fareneheit)
    """
    if temp > 140 or temp < 0:
        temp = None

    return temp


def twoTempAverage(temp1, temp2):
    """
    Average two temperatures, properly handling values that are None
    or out of range
    """

    # Apply temperature sanity checks (assuming temp in degrees
    # Fareneheit)
    temp1 = tempRangeCheck(temp1)
    temp2 = tempRangeCheck(temp1)

    # Calculate average
    if temp1 is None and temp2 is None:
        temp = None
    elif temp1 is None:
        temp = float(temp2)
    elif temp2 is None:
        temp = float(temp1)
    else:
        temp = float( temp1 + temp2 ) / 2
    return temp


def calculateAWC_RainIrrigation(crop_season, 
                                field, 
                                date, 
                                water_history_query=None):

    if water_history_query is None:
        water_history_query = WaterHistory.objects.filter(crop_season=crop_season,
                                                          field_list=field).all()

    wh_list = water_history_query.filter(date=date).all()

    if wh_list:
        rainfall   = sum( map( lambda wh: wh.rain, wh_list ) )
        irrigation = sum( map( lambda wh: wh.irrigation, wh_list) )
        return ( rainfall, irrigation )
    else:
        return ( 0.0, 0.0 )


def quantize( f ):
    """ Convert to a Decimal with resolution of 0.01 """
    # An issue within the python Decimal class causes conversion from
    # Decimal to Decimal to fail if the module is reloaded.  Work
    # around that issue by converting to string, then to a Decimal.
    retval = Decimal(str(f)).quantize( Decimal('0.01') )

    return retval

OPTIMIZE=True

def generate_water_register(crop_season, 
                            field, 
                            user, 
                            start_date=None, 
                            end_date=None):

    ####
    ## Determine planting date, and stop calculation if no planting has been done
    planting_event = CropSeasonEvent.objects.filter(crop_season=crop_season,
                                                        field=field,
                                                        crop_event__name='Planting').order_by("-date").first()

    if not planting_event: return (None, None)
    ####


    ####
    ## Determine the and last first event date to show
    if start_date is None:
        start_date = planting_event.date

    if end_date is None:
        if COMPUTE_FULL_SEASON:
            end_date = crop_season.season_end_date + timedelta(1)
        else:
            today_plus5 = date.today() + timedelta(days=5)
            end_date = min(today_plus5, crop_season.season_end_date)
    ####




    
    ####
    ## Cache values / queries for later use
    probe = Probe.objects.get(crop_season=crop_season, field_list=field)
    radio_id = probe.radio_id
    probe_reading_query       = ProbeReading.objects.filter(radio_id=radio_id).all()
    soil_type_parameter_query = SoilTypeParameter.objects.filter(soil_type=field.soil_type).all()
    water_history_query       = WaterHistory.objects.filter(crop_season=crop_season,
                                                            field_list=field).all()
    crop_season_events_query = CropSeasonEvent.objects.filter(crop_season=crop_season, 
                                                              crop_season__field_list=field).distinct().all()
    ####


    wr_query = WaterRegister.objects.filter(crop_season=crop_season,
                                            field=field, 
                                            date__gte=start_date,
                                            date__lte=end_date).all()

    maxWater = float(field.soil_type.max_available_water)

    ## Assume that each field starts with a full water profile
    AWC_initial = maxWater


    ## First pass, calculate water profile (AWC)
    temps_since_last_water_date = []
    wr_prev = None
    for  date in daterange(start_date, end_date):
        ####
        ## Get AWC for yesterday
        ##
        yesterday = date - timedelta(days=1)

        ## Check if we have (cached) the water register object for
        ## yesterday, if so grab the AWC, otherwise use the default
        ## maximum for the soil type
        if (wr_prev is None) or (wr_prev.date != yesterday): 
            try:
                wr_prev = wr_query.filter(date=date)[0]
                AWC_prev = wr_prev.average_water_content
            except ( ObjectDoesNotExist,  IndexError, ):
                AWC_prev = AWC_initial
        else:
            AWC_prev = wr_prev.average_water_content
        ####
        
        ####
        ## Get or Create a water register object (db record) for today
        try: 
            wr = wr_query.filter(date=date)[0]
        except ( ObjectDoesNotExist,  IndexError, ):
            wr = WaterRegister(
                crop_season = crop_season,
                field = field,
                date = date
            )
        ##
        ####

        ####
        ## Copy information from crop event record 
        cse = crop_season_events_query.filter(date__lte=date).distinct().order_by('-date').first()
        ce = cse.crop_event

        wr.crop_stage      = ce.name
        wr.daily_water_use = ce.daily_water_use
        wr.max_temp_2in    = ce.max_temp_2in
        wr.irrigate_to_max = ce.irrigate_to_max
        wr.do_not_irrigate = ce.do_not_irrigate
        wr.message         = ce.irrigation_message
        ##
        ####

        ####
        ## Get (automatic) probe reading information and calculate AWC
        AWC_probe, temp = calculateAWC_ProbeReading(crop_season, field, date, 
                                                    probe=probe, 
                                                    probe_reading_query=probe_reading_query, 
                                                soil_type_parameter_query=soil_type_parameter_query)
        ##
        ####

        ####
        ## Get (manually entered) water register entries
        wr.rain, wr.irrigation  = calculateAWC_RainIrrigation(crop_season, field, date, 
                                                              water_history_query=water_history_query)
        AWC_register = float(AWC_prev) - float(wr.daily_water_use) + float(wr.rain) + float(wr.irrigation)
        ##
        ####

        ####
        ## Prefer AWC from probe reading over AWC from water registry
        if AWC_probe is not None: 
            wr.average_water_content = float(AWC_probe)
            wr.computed_from_probes  = True
        else:
            wr.average_water_content = float(AWC_register)
            wr.computed_from_probes  = False
        ##
        ####

        ## Enforce maximum soil water content based on soil type
        if wr.average_water_content > maxWater: 
            wr.average_water_content = maxWater

        ## Store user into accounting info..
        if wr.cuser_id is None:
            wr.cuser_id = user.pk
        wr.muser_id = user.pk

        ## Write to the database
        wr.save()
        
        ## Calculate and store max temperature since last appreciable rainfall or irrigation
        if wr.average_water_content >= AWC_prev + 0.1:
            # Max temp is only today's value 
            wr.max_observed_temp_2in = temp

            # Reset max temp calculation
            temps_since_last_water_date = []
        else:
            # Add today's temperature
            temps_since_last_water_date.append(temp)

            # Calculate max temp
            wr.max_observed_temp_2in = max(temps_since_last_water_date)

        ## Cache this entry for tomorrow
        wr_prev = wr

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
            ####
            ## Check if wee need to irrigate *today*

            # never irrigate if flag is set
            if wr.do_not_irrigate:
                wr.irrigate_flag = False
            else:
                # Too dry:
                if wr.average_water_content < 0.00:
                    wr.irrigate_flag = True
            
                # Too hot:
                if wr.max_temp_2in is not None and \
                   wr.max_observed_temp_2in is not None and \
                   wr.max_observed_temp_2in > wr.max_temp_2in:
                    wr.irrigate_flag = True
                    wr.too_hot_flag  = True

                ####
                ## Check if we need to irrigate in the next five days
                ####
                wr.check_sensors_flag = False

                date_plus5 = date + timedelta(days=5)
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
