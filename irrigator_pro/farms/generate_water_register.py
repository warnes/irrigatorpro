from django.utils import timezone

import datetime

import os, os.path
import math
import sys
import time
from decimal import Decimal
from numpy import nanmean

from irrigator_pro.settings import ABSOLUTE_PROJECT_ROOT, COMPUTE_FULL_SEASON, WATER_REGISTER_DELTA
from farms.models import *
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(days=n)



########################################################################
## Calculate the AWC based on probe reading for a given crop_season,
## date and field.
##
## There can be more than one probe for a given field/date. As of
## now it looks like multiple probes will have different soil depth,
## but we will play it safe and have code to average in case multiple
## probes are used for the same depth. If the initial assumption
## holds true (only one probe / depth) then averaging will give the
## correct results.
########################################################################

def calculateAWC_ProbeReading(crop_season,
                              field,
                              date):
    """
    Calculate the Available Water Content for the specified field and date
    from Probe Reading data (if available).  If no probe reading
    exists, returns None.

    Also returns the temperature, so that the return value is a tuple
    of (AWC, temp)
    """

    probes = Probe.objects.filter(crop_season=crop_season, field_list=field).all()
    radio_ids = []
    if len(probes) == 0:
        return ( None, None )
    else:
        for probe in probes:
            radio_ids.append(probe.radio_id)
    
    # Make sure radio ids are unique
    radio_ids = list(set(radio_ids))


    ## Get the maximum root depth
    if crop_season:
        crop = crop_season.crop
        max_root_depth = crop_season.crop.max_root_depth
    else:
        return ( None, None )


    ## Collect all the probe readings: for each radio ID keep one only one probe reading 
    ## from the date sent as parameter. If there is more than one keep the latest.


    probe_readings = []
    for r_id in radio_ids:
        probe_reading = ProbeReading.objects.filter(radio_id=r_id,
                                                    reading_datetime__startswith=date).order_by('reading_datetime').last()

        if  probe_reading:
            probe_readings.append(probe_reading)

            
    if len(probe_readings) == 0:
        return ( None, None )

    ## Extract soil parameters
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


    ## Loop through probe readings. Only keep values when reading >0

    ### Loop here through loop readings for all the probes given day.

    AWC_8_l  = []
    AWC_16_l = []
    AWC_24_l = []

    ### Have to be a icer way to write this... lambda calculus?
    for probe_reading in probe_readings:

        AWC_8_l.append ( soil_type_8in.slope  * ( safelog( abs(probe_reading.soil_potential_8) )  - ln40 ) * 24 )
        AWC_16_l.append( soil_type_16in.slope * ( safelog( abs(probe_reading.soil_potential_16) ) - ln40 ) * 24 )
        AWC_24_l.append( soil_type_24in.slope * ( safelog( abs(probe_reading.soil_potential_24) ) - ln40 ) * 24 )

    AWC_8  = min(AWC_8_l)
    AWC_16 = min(AWC_16_l)
    AWC_24 = min(AWC_24_l)

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


##
# Determine the earliest water register to update. This is based
# on the modification dates for the WaterHistory, ProbeReadings,
# and WaterRegister. Want to allow for a WaterHistory or ProbeReading
# to be entered or modified long after the date of the event.
def earliest_register_to_update(report_date,
                                crop_season,
                                field):

    # Start by getting the dependency modification date stored in the field object
    dependency_mdate = field.earliest_changed_dependency_date

    # Get the modification time of the latest water register
    latest_water_register = WaterRegister.objects.filter(crop_season=crop_season,
                                                         field=field
                                                     ).order_by('-date').first()
    if latest_water_register is None:
        print 'No water register yet'
        return crop_season.season_start_date
    
    print 'Date of latest wr: ', latest_water_register.date



    # Get the earliest water history that has been modified after the latest
    # water register has been modified

    earliest_wh_update = WaterHistory.objects.filter(crop_season=crop_season,
                                          field_list=field).filter(Q(mdate__gte = latest_water_register.mdate)).order_by('date').first()

    earliest_to_update = latest_water_register.date + timedelta(days=1)
    if earliest_wh_update is None:
        print 'No WH will cause update to water register'
    else:
        earliest_to_update = earliest_wh_update.date

    # Get the earliest probe reading that has been modified after the latest
    # water register has been modified
        
    try:
        probe_list = Probe.objects.filter(crop_season=crop_season, field_list=field).all()

        earliest_changed_probe = None
        for probe in probe_list:
            earliest_changed = ProbeReading.objects.filter(radio_id=probe.radio_id).filter(Q(mdate__gte = latest_water_register.mdate)).order_by('reading_datetime').first()

            if earliest_changed_probe is None:
                earliest_changed_probe = earliest_changed
            else:
                if earliest_changed is not None and earliest_changed.reading_datetime < earliest_changed_probe.reading_datetime:

                
                    earliest_changed_probe = earliest_changed

        if earliest_changed_probe is None:
            print 'No probe will cause update (nothing changed)'
        else:
            if earliest_changed_probe.reading_datetime.date() < earliest_to_update:
                earliest_to_update = earliest_changed_probe.reading_datetime.date()
                print 'Update caused by updated probe reading'
            else:
                print 'Probe will not cause update (wh even earlier)'

    except ObjectDoesNotExist:
        print 'No probe will cause update in water register (no probe)'

    print "Caclulated dependency dates:"
    print "field.earliest_changed_dependency_date:", dependency_mdate
    print "earliest changed probe:", earliest_to_update
    print "latest_water_register.date + 1:", latest_water_register.date + timedelta(1)

    return min(dependency_mdate, earliest_to_update, latest_water_register.date + timedelta(1))

        



# In order to test we change the definition of "Today". It is passed
# as a parameter, set to current day if not defined.
def generate_water_register(crop_season, 
                            field, 
                            user, 
                            start_date=None, 
                            report_date=None):

    ####
    ## Determine planting date, and stop calculation if no planting has been done
    planting_event = CropSeasonEvent.objects.filter(crop_season=crop_season,
                                                        field=field,
                                                        crop_event__name='Planting').order_by("-date").first()


    if not planting_event: return (None, None)
    ####




    ####
    ## Determine the first and last first event date to show
    if start_date is None:
        start_date = planting_event.date

    if report_date is None:
        report_date = datetime.date.today();

    if COMPUTE_FULL_SEASON:
        end_date = crop_season.season_end_date + timedelta(1)
    else:
        today_plus_delta = report_date + timedelta(days=WATER_REGISTER_DELTA)
        latest_water_register = WaterRegister.objects.filter(crop_season=crop_season,
                                                             field=field
                                                             ).order_by('-date').first()

        end_date = min( max(today_plus_delta, latest_water_register.date), crop_season.season_end_date) + timedelta(1)
    
    ####



    ####
    ## Cache values / queries for later use


    # try:
    #     probe = Probe.objects.get(crop_season=crop_season, field_list=field)
    #     radio_id = probe.radio_id
    # except ObjectDoesNotExist:
    #     probe = None
    #     radio_id = None


    water_history_query       = WaterHistory.objects.filter(crop_season=crop_season,
                                                            field_list=field).all()
    crop_season_events_query = CropSeasonEvent.objects.filter(crop_season=crop_season, 
                                                              crop_season__field_list=field).distinct().all()
    ####

    ## Find out what is the earliest water register to update, based on modification dates.

    earliest = earliest_register_to_update(report_date, crop_season, field)


    wr_query = WaterRegister.objects.filter(crop_season=crop_season,
                                            field=field, 
                                            date__gte=earliest,
                                            date__lte=end_date).all()

    maxWater = float(field.soil_type.max_available_water)

    if earliest <= crop_season.season_start_date:
        ## Assume that each field starts with a full water profile
        AWC_initial = maxWater
    else:
        try:
            wr_yesterday = WaterRegister.objects.get(crop_season=crop_season,
                                                     field=field,
                                                     date=earliest - timedelta(days=1)
                                                     )
            AWC_initial = wr_yesterday.average_water_content
        except:
            raise RuntimeError("No previous water_register record on " + earliest );

    ## First pass, calculate water profile (AWC)
    temps_since_last_water_date = []
    wr_prev = None

    ## Some optimization to do here: After the first pass we know the prev record is there.
    first_process_date = earliest
    for  date in daterange(first_process_date, end_date):
        ####
        ## Get AWC for yesterday, and copy the irrigate_to_max_seen, irrigate_to_max_achieved flags
        ##
        yesterday = date - timedelta(days=1)

        ## Check if we have (cached) the water register object for
        ## yesterday, if so grab the AWC, otherwise use the default
        ## maximum for the soil type
        if (wr_prev is None) or (wr_prev.date != yesterday): 
            try:
                wr_prev = wr_query.filter(date=yesterday)[0]
                AWC_prev = wr_prev.average_water_content
                irrigate_to_max_seen_prev = wr_prev.irrigate_to_max_seen
                irrigate_to_max_achieved_prev = wr_prev.irrigate_to_max_achieved
            except ( ObjectDoesNotExist,  IndexError, ):
                AWC_prev = AWC_initial
                irrigate_to_max_seen_prev = False
                irrigate_to_max_achieved_prev = False

        else:
            AWC_prev = wr_prev.average_water_content
            irrigate_to_max_seen_prev = wr_prev.irrigate_to_max_seen
            irrigate_to_max_achieved_prev = wr_prev.irrigate_to_max_achieved

            irrigate_to_max_seen_prev = wr_prev.irrigate_to_max_seen
            irrigate_to_max_achieved_prev = wr_prev.irrigate_to_max_achieved



        ####
        

        ####
        ## Get or Create a water register object (db record) for today
        try: 
            wr = wr_query.filter(date=date)[0]

            computed_from_probes  = False
            irrigate_flag         = False
            too_hot_flag          = False
            check_sensors_flag    = False
            dry_down_flag         = False

            
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
	if cse is None: return
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

        #AWC_probe = None
        #temp = None

        # Could return (None, None) if there are no probes.
        # Moved this validation to calculateAWC_ProbeReading,
        # since there is already code to validate.
        AWC_probe, temp = calculateAWC_ProbeReading(crop_season,
                                                    field,
                                                    date) 

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

        ## Store userwa into accounting info..
        if wr.cuser_id is None:
            wr.cuser_id = user.pk
        wr.muser_id = user.pk


        ## Write to the database
        wr.save()
        
        ## Calculate and store max temperature since last appreciable rainfall or irrigation
        if wr.average_water_content >= float(AWC_prev) + 0.1:
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
                                            date__gte=earliest,
                                            date__lte=end_date).all()
        
    ## Second pass, calculate flags 
    irrigate_to_max_flag_seen = False
    irrigate_to_max_achieved  = False
    drydown_flag              = False
    irrigate_to_max_days      = 0
    for date in daterange(first_process_date, end_date):

        wr = wr_query.filter(date=date)[0]

        ## Will handle both the case where the first irrigate_to_flag set to 
        ## true was in a register not updated for this report.
        if wr.irrigate_to_max or wr.irrigate_to_max_seen: 
            irrigate_to_max_flag_seen = True
            wr.irrigate_to_max_seen = True

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
                wr.days_to_irrigation = -1 # Just in case it had been changed previously
                if wr.average_water_content <= 0.00:
                    wr.irrigate_flag = True
                    wr.days_to_irrigation = 0
            
                # Too hot:
                if wr.max_temp_2in is not None and \
                   wr.max_observed_temp_2in is not None and \
                   wr.max_observed_temp_2in > wr.max_temp_2in:
                    wr.irrigate_flag = True
                    wr.days_to_irrigation = 0
                    wr.too_hot_flag  = True

                ####
                ## Check if we need to irrigate in the next few days, based on WATER_REGISTER_DELTA
                ####
                wr.check_sensors_flag = False
                if wr.days_to_irrigation < 0:
                    date_plus_delta = date + timedelta(days=(WATER_REGISTER_DELTA+1))
                    for date_future in daterange(date + timedelta(days=1), date_plus_delta):
                        try:
                            wr_future = wr_query.get(date=date_future)
                            #wr.check_sensors_flag = wr.check_sensors_flag or (wr_future.average_water_content <= 0.00)
                            if ( wr_future.average_water_content <= 0.00 ) and ( wr_future.do_not_irrigate == False ):
                                wr.check_sensors_flag = True
                                wr.days_to_irrigation = (date_future - date).days
                                break
                        except ObjectDoesNotExist:
                            pass

        else:  # execute below if irrigate_to_max_flag_seen is true
            if wr.irrigate_to_max_achieved or irrigate_to_max_achieved or irrigate_to_max_days >= 3:
                wr.irrigate_flag = False
                wr.dry_down_flag = True
            else:
                irrigate_to_max_days += 1
                if wr.average_water_content >= maxWater:
                    wr.irrigate_to_max_achieved = True
                    irrigate_to_max_achieved = True
                    wr.irrigate_flag         = False
                    wr.check_sensors_flag    = False
                    wr.dry_down_flag         = True
                else:
                    wr.irrigate_flag      = True
                    wr.check_sensors_flag = True

        wr.save()

    return
