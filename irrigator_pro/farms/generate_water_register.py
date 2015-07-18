import math
import sys
from decimal import Decimal
from numpy import nanmean
from datetime import date, datetime, timedelta


from irrigator_pro.settings import ABSOLUTE_PROJECT_ROOT, COMPUTE_FULL_SEASON, WATER_REGISTER_DELTA, DEBUG
from farms.models import *
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

from common.utils import daterange, minNone, safelog, quantize

from farms.utils import get_probe_readings_dict

# workarounds for the absence of query datetime__date operator
from common.utils import d2dt_min, d2dt_max, d2dt_range 

LN40 = math.log(40.0)


##########################################################################
## Calculate the AWC based on probe reading and manual entries for a given
## crop_season, date and field.
##
## There can be more than one probe for a given field/date. As of
## now it looks like multiple probes will have different soil depth,
## but we will play it safe and have code to average in case multiple
## probes are used for the same depth. If the initial assumption
## holds true (only one probe / depth) then averaging will give the
## correct results.
##########################################################################

def calculateAWC(crop_season,
                 field,
                 date,
                 water_history_query,
                 probe_readings):
    """
    Calculate the Available Water Content for the specified field and date
    from Probe Reading data (if available) and WaterHistory (or manual
    entries, if available).

    Also returns the temperature, so that the return value is a tuple
    of (AWC, temp)
    """

    if isinstance(date, datetime):
        date = date.date()

    ## Get the maximum root depth
    if crop_season:
        crop = crop_season.crop
        max_root_depth = crop_season.crop.max_root_depth
    else:
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


    ## Loop through probe readings. Only keep values when reading >0

    ### Loop here through loop readings for all the probes given day.


    def AWC(slope, potential):
        return slope * 24 * ( safelog( abs(potential) )  - LN40 ) 


    latest_measurement_date = datetime( date - timedelta(days=1))

    AWC_8  = None
    AWC_16 = None
    AWC_24 = None


    if date in probe_readings:
        for probe_reading in probe_readings[date]:
            if probe_reading.datetime > latest_measurement_date:
                if probe_reading.soil_potential_8:
                    AWC_8_l = AWC( soil_type_8in.slope,  probe_reading.soil_potential_8 )
                if probe_reading.soil_potential_16:
                    AWC_16 = AWC( soil_type_16in.slope, probe_reading.soil_potential_16)
                if probe_reading.soil_potential_24:
                    AWC_24 = AWC( soil_type_24in.slope, probe_reading.soil_potential_24)
                latest_measurement_date = probe_reading.datetime


    ## Now get the potentials based on water history
    for wh in water_history_query.filter(datetime__range=d2dt_range(date)).all():
        if probe_reading.datetime > latest_measurement_date:
            if wh.soil_potential_8:
                AWC_8 = AWC( soil_type_8in.slope,  wh.soil_potential_8 )
            if wh.soil_potential_16:
                AWC_16 = AWC( soil_type_8in.slope,  wh.soil_potential_16 )
            if wh.soil_potential_24:
                AWC_8_l = AWC( soil_type_8in.slope,  wh.soil_potential_24 )


    ### If any of the AWC has no value returns nothing

    if not AWC_8 or not AWC_16 or not AWC_24:
        return (None, None)
    

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
        AWC = (AWC_8 + AWC_16 + AWC_24) / 3


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



def calculateAWC_min(crop_season,
                     field):
    """
    Calculate the minimum Available Water Content for the specified field.
    """

    ## Get the maximum root depth
    if crop_season:
        crop = crop_season.crop
        max_root_depth = crop_season.crop.max_root_depth
    else:
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


    def AWC(slope, potential):
        return slope * 24 * ( safelog( abs(potential) )  - LN40 ) 

    AWC_8_min  = AWC( soil_type_8in.slope,  200 ) 
    AWC_16_min = AWC( soil_type_16in.slope, 200 )
    AWC_24_min = AWC( soil_type_24in.slope, 200 )

    #####
    ## Calculate average AWC_min at the depths accessible to the crop
    ## roots.
    #####
    ## NB: This would probably be better done via a linear
    ##     interpolation, rather than discrete steps.
    if max_root_depth <= 8:
        AWC_min = AWC_8_min
    elif max_root_depth <= 16:
        AWC_min = (AWC_8_min + AWC_16_min) / 2
    else: # max_root_depth > 16
        AWC_min = (AWC_8_min + AWC_16_min + AWC_24_min) / 3

    return (AWC_min)


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


def calculate_total_RainIrrigation(crop_season, 
                                   field, 
                                   date, 
                                   water_history_query,
                                   probe_readings):

    """
    Calculate total rain/irrigations. Values are added over all records
    for that day. Two queries are required, since rain/irrigation can now
    come from the probe readings as well.
    """

    if isinstance(date, datetime):
        date = date.date()

    rainfall = Decimal(0.0)
    irrigation = Decimal(0.0)


    # First calculate the rainfall/irrigation coming from probe readings
    if date in probe_readings:
        if DEBUG: print "Have probe readings for ", date
        rainfall = sum( map( lambda pr: pr.rain, probe_readings[date]))
        irrigation = sum( map( lambda pr: pr.irrigation, probe_readings[date]))

        if DEBUG: print "Rainfall, irrigation from probes" , rainfall, ", ", irrigation

    else:
        print date, " has no probe readings"
    

    # Now add the values coming from the water history (soon to be renamed manual reading)
    wh_list = water_history_query.filter(datetime__range=d2dt_range(date)).all()
    if wh_list:
        rainfall   = rainfall + sum( map( lambda wh: wh.rain, wh_list ) )
        irrigation = irrigation + sum( map( lambda wh: wh.irrigation, wh_list) )

    if DEBUG: print "Returning ", rainfall, ", ", irrigation
    return ( rainfall, irrigation )




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

    if DEBUG: print "Earliest changed date:", dependency_mdate

    # Get the modification time of the latest water register
    latest_water_register = WaterRegister.objects.filter(crop_season=crop_season,
                                                         field=field
                                                     ).order_by('-datetime').first()
    if latest_water_register is None:
        if DEBUG: print 'No water register yet'
        return crop_season.season_start_date
    
    if DEBUG: print 'Date of latest wr: ', latest_water_register.datetime.date()



    # Get the earliest water history that has been modified after the latest
    # water register has been modified

    earliest_wh_update = WaterHistory.objects.filter(crop_season=crop_season,
                                                     field=field).filter(
                               Q(mdate__gte = latest_water_register.mdate)).order_by('datetime').first()

    earliest_to_update = latest_water_register.datetime.date() + timedelta(days=1)
    if earliest_wh_update is None:
        if DEBUG: print 'No WH will cause update to water register'
    else:
        earliest_to_update = earliest_wh_update.datetime.date()

    # Get the earliest probe reading that has been modified after the latest
    # water register has been modified
        
    try:
        probe_list = Probe.objects.filter(crop_season=crop_season, field=field).all()

        earliest_changed_probe = None
        for probe in probe_list:
            earliest_changed = ProbeReading.objects.filter(radio_id=probe.radio_id).filter(Q(mdate__gte = latest_water_register.mdate)).order_by('datetime').first()

            if earliest_changed_probe is None:
                earliest_changed_probe = earliest_changed
            else:
                if earliest_changed is not None and earliest_changed.datetime < earliest_changed_probe.datetime:
                    earliest_changed_probe = earliest_changed

        if earliest_changed_probe is None:
            if DEBUG: print 'No probe will cause update (nothing changed)'
        else:
            if earliest_changed_probe.datetime.date() < earliest_to_update:
                earliest_to_update = earliest_changed_probe.datetime.date()
                if DEBUG: print 'Update caused by updated probe reading'
            else:
                if DEBUG: print 'Probe will not cause update (wh even earlier)'

    except ObjectDoesNotExist:
        if DEBUG: print 'No probe will cause update in water register (no probe)'

    if DEBUG: print "Caclulated dependency dates:"
    if DEBUG: print "field.earliest_changed_dependency_date:", dependency_mdate
    if DEBUG: print "earliest changed probe:", earliest_to_update
    if DEBUG: print "latest_water_register.date + 1:", latest_water_register.datetime.date() + timedelta(1)

    return minNone(dependency_mdate, earliest_to_update, 
                   latest_water_register.datetime.date() + timedelta(1))


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
    ##
    ####

    ####
    ## Determine the first and last first event date to show
    if start_date is None:
        start_date = planting_event.date

    if report_date is None:
        report_date = datetime.now().date()

    if COMPUTE_FULL_SEASON:
        end_date = crop_season.season_end_date + timedelta(1)
    else:
        today_plus_delta = report_date + timedelta(days=WATER_REGISTER_DELTA)
        latest_water_register = WaterRegister.objects.filter(crop_season=crop_season,
                                                             field=field
                                                             ).order_by('-datetime').first()

        if latest_water_register:
            last_register_date = max(today_plus_delta, latest_water_register.datetime.date())
        else:
            last_register_date = today_plus_delta

        end_date = min(last_register_date, crop_season.season_end_date) + timedelta(1)
    ##
    ####


    probe_readings = get_probe_readings_dict(field, crop_season, start_date, report_date)


    ####
    ## Cache values / queries for later use

    water_history_query       = WaterHistory.objects.filter(crop_season=crop_season,
                                                            field=field).all()
    crop_season_events_query = CropSeasonEvent.objects.filter(crop_season=crop_season, 
                                                              crop_season__field_list=field).distinct().all()
    ####

    ## Find out what is the earliest water register to update, based on modification dates.

    first_process_date = earliest_register_to_update(report_date, crop_season, field)


    wr_query = WaterRegister.objects.filter(crop_season=crop_season,
                                            field=field, 
                                            datetime__gte=d2dt_min(first_process_date),
                                            datetime__lte=d2dt_max(end_date)
                                            ).all()

    maxWater = float(field.soil_type.max_available_water)
    minWater = calculateAWC_min( crop_season, field )

    if first_process_date <= crop_season.season_start_date:
        ## Assume that each field starts with a full water profile
        AWC_initial = maxWater
    else:
        try:
            wr_yesterday = WaterRegister.objects.get(crop_season=crop_season,
                                                     field=field,
                                                     datetime__range=d2dt_range(first_process_date - timedelta(days=1))
                                                     )
            AWC_initial = wr_yesterday.average_water_content
        except:
            raise RuntimeError("No previous water_register record on " + first_process_date );

    ## First pass, calculate water profile (AWC)
    if DEBUG: print "First pass, calculate water profile (AWC)"
    temps_since_last_water_date = []
    wr_prev = None

    if DEBUG: print "Date range: %s to %s" % (first_process_date, end_date)
    ## Some optimization to do here: After the first pass we know the prev record is there.
    for  date in daterange(first_process_date, end_date):
        if DEBUG: print "  Working on ", date
        ####
        ## Get AWC for yesterday, and copy the irrigate_to_max_seen, irrigate_to_max_achieved flags
        ##
        yesterday = date - timedelta(days=1)

        ## Check if we have (cached) the water register object for
        ## yesterday, if so grab the AWC, otherwise use the default
        ## maximum for the soil type
        if (wr_prev is None) or (wr_prev.date != yesterday): 
            try:
                wr_prev = wr_query.filter(datetime__range=d2dt_range(yesterday))[0]
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
        
        ## Delete previous water register entries
        # wr_query.filter(datetime__range=d2dt_range(date)).delete()
        # wr = WaterRegister(crop_season = crop_season,
        #                    field = field,
        #                    datetime__range = d2dt_range(date)
        #                    )

        try: 
            wr = wr_query.filter(datetime__range=d2dt_range(date))[0]

            computed_from_probes  = False
            irrigate_flag         = False
            too_hot_flag          = False
            check_sensors_flag    = False
            dry_down_flag         = False

            # clear out existing flags
            wr.irrigate_flag = False
            wr.too_hot_flag  = False
            wr.days_to_irrigation = -1
            wr.check_sensors_flag = False
            
        except ( ObjectDoesNotExist,  IndexError, ):
            wr = WaterRegister(
                crop_season = crop_season,
                field = field,
                datetime = d2dt_min(date)
            )
        
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
        # Moved this validation to calculateAWC,
        # since there is already code to validate.
        AWC_probe, temp = calculateAWC(crop_season,
                                       field,
                                       date,
                                       water_history_query,
                                       probe_readings) 
        if DEBUG: print "  AWC_probe=", AWC_probe
        ##
        ####

        ####
        ## Get (manually entered) water register entries
        wr.rain, wr.irrigation  = calculate_total_RainIrrigation(crop_season,
                                                                 field,
                                                                 date, 
                                                                 water_history_query,
                                                                 probe_readings)

        # wr.min_temp_24_hours, wr.max_temp_24_hours = calculate_min_max_24_hours(crop_season,
        #                                                                         field,
        #                                                                         date,
        #                                                                         water_history_query,
        #                                                                         probe_readings)

        
        AWC_register = float(AWC_prev) - float(wr.daily_water_use) + float(wr.rain) + float(wr.irrigation)
        if DEBUG: print "  AWC_register=", AWC_register
        ##
        ####

        ####
        ## Prefer AWC from probe reading over AWC from water registry
        if AWC_probe is not None: 
            wr.average_water_content = quantize(AWC_probe)
            wr.computed_from_probes  = True
        else:
            wr.average_water_content = quantize(AWC_register)
            wr.computed_from_probes  = False
        if DEBUG: print "  wr.average_water_content=", wr.average_water_content
        if DEBUG: print "  wr.computed_from_probes=", wr.computed_from_probes
        ##
        ####

        ## Enforce min and maximum soil water content based on soil type
        if wr.average_water_content > maxWater: 
            if DEBUG: print "  Enforce max soil AWC: ", maxWater
            wr.average_water_content = maxWater

        if wr.average_water_content < minWater: 
            if DEBUG: print "  Enforce min soil AWC: ", minWater
            wr.average_water_content = minWater

        ## Store user into accounting info..
        if wr.cuser_id is None:
            wr.cuser_id = user.pk
        wr.muser_id = user.pk


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

        ## Write to the database
        if DEBUG: print "  saving..."
        wr.save()

    ## Refresh query
    wr_query = WaterRegister.objects.filter(crop_season=crop_season,
                                            field=field, 
                                            datetime__gte=d2dt_min(first_process_date),
                                            datetime__lte=d2dt_max(end_date)
                                            ).all()
        
    ## Second pass, calculate flags 
    if DEBUG: print "Second pass, calculate flags"
    irrigate_to_max_flag_seen = False
    irrigate_to_max_achieved  = False
    drydown_flag              = False
    irrigate_to_max_days      = 0
    for date in daterange(first_process_date, end_date):
        if DEBUG: print "  Working on ", date

        wr = wr_query.filter(datetime__range=d2dt_range(date))[0]

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
            ## Check if we need to irrigate *today*

            # clear out existing flags
            wr.irrigate_flag = False
            wr.too_hot_flag  = False
            wr.days_to_irrigation = -1
            wr.check_sensors_flag = False

            # never irrigate if flag is set
            if wr.do_not_irrigate:
                wr.irrigate_flag = False
            else:
                # Too dry:
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
                            wr_future = wr_query.get(datetime__range=d2dt_range(date_future))
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

        ## Write to the database
        if DEBUG: print "saving..."
        wr.save()


    # reset the dependency date
    field.earliest_changed_dependency_date = None
    field.save()

    return
