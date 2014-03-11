#!/usr/bin/env python
import datetime
import os, os.path
import math
import sys
import time

"""
This script downlaads the UGA SSA data stored on the NESPAL webserver and uploads it into the IrrigatorPro database.
"""

try:
    # Add the directory *above* this to the python path so we can find our modules
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "irrigator_pro.settings")
except: # assume we're running in the script directory
    sys.path.append("..")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "irrigator_pro.settings")


from irrigator_pro.settings import ABSOLUTE_PROJECT_ROOT
from farms.models import *
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

## Cache soil type parameter information
soilTypeParametersQuery = SoilTypeParameter.objects.all()
bool(soilTypeParametersQuery)

def calculateAWC_ProbeReading(field, date):
    """
    Calculate the Available Water Content for the specified field and
    date from Probe Reading data (if available).  If no probe reading
    exists, returns None.
    """

    ## Find the probe/radio_id for this field (if any)
    try:
        probe = Probe.objects.get(field_list=field)
    except ObjectDoesNotExist:
        return None

    radio_id = probe.radio_id

    ## Determine the crop that corresponds to this date
    crop_season = CropSeason.objects.filter(field_list=field,
                                            season_start_date__lte=date,
                                            season_end_date__gte=date,
                                            )
    if( crop_season.count() > 1 ):
        raise RuntimeError("More than one crop season for field '%s' on %s." % (field, date))
    crop_season = crop_season.first()

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

    if AWC_8  > field.soil_type.max_available_water: AWC_8  = field.soil_type.max_available_water
    if AWC_16 > field.soil_type.max_available_water: AWC_16 = field.soil_type.max_available_water
    if AWC_24 > field.soil_type.max_available_water: AWC_24 = field.soil_type.max_available_water

    #print 'AWC  8"=%4.2f' % AWC_8
    #print 'AWC 16"=%4.2f' % AWC_16
    #print 'AWC 24"=%4.2f' % AWC_24

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


def caclulateAWC_RainIrrigation(field, date):

    wh = WaterHistory.objects.filter(field_list=field,
                                     date=date
                                    ).last()

    if wh:
        return ( wh.rain, wh.irrigation )
    else:
        return ( 0.0, 0.0 )


def get_daily_water_use(field, date):
    cse = CropSeasonEvent.objects.filter(crop_season__field_list=field,
                                         date__lte=date).distinct().order_by('-date').first()
    dwu = cse.crop_event.daily_water_use
    return dwu


if __name__ == "__main__":

    time_start = time.time()

    farm  = Farm.objects.get(pk=1)
    field = Field.objects.filter(farm=farm).first()

    crop_season = CropSeason.objects.get(name="Corn 2013")

    ## Determine the first event date (planting) to show
    planting_event = CropSeasonEvent.objects.filter(crop_season=crop_season,
                                                    field=field,
                                                    date__lte=date,
                                                    crop_event__name='Planting').order_by("-date").first()
    start_date = planting_event.date

    ## Determine the last event date (end of season) to show
    end_date = crop_season.season_end_date

    AWC_initial = float(field.soil_type.max_available_water)

    out = ""

    out += "\n"
    out += "\n" + "** Farm         : %s" % farm
    out += "\n" + "** Field        : %s" % field
    out += "\n" + "** Starting AWC : %s" % AWC_initial
    out += "\n"
    #out += "\n" + "%10s | %5s | "  % ("Date", "DWU", )


    date = start_date
    AWC_prev = AWC_initial
    while date <= end_date:
        out += "\n" + "Date: %s  " % date

        DWU = float(get_daily_water_use(field, date))
        out += "%+4.2f  " % -DWU

        AWC = calculateAWC_ProbeReading(field, date)
        if AWC:
            AWC_plus = float("NaN")
            out += "%13s = %6.2f (from probes)" % ( "", AWC )
        else:
            AWC_plus = caclulateAWC_RainIrrigation(field, date)
            AWC = AWC_prev + float(AWC_plus[0]) + float(AWC_plus[1])
            out += "%5.2f + %5.2f = %6.2f" % ( #AWC_prev,
                                              AWC_plus[0],
                                              AWC_plus[1],
                                              AWC-DWU )
        AWC_prev = AWC-DWU

        date += datetime.timedelta(days=1)

    time_end = time.time()

    out += "\n"
    out += "\n" + "Elapsed time: %4.2f" % ( time_end - time_start )
    out += "\n"


## Need to construct a table with the following fields:
#
# Grouping:
#   Farm,
#   Field,
#   Date,
#
# Soil & Probe Information
#   Soil Type
#
# Water Debits:
#   Growth Stage
#   Daily Water Use
#
# Probe Information:
#   soil_potential_8,
#   soil_potential_16,
#   soil_potential_24,
#
# Water Credits:
#   rain,
#   irrigation,
#
# Water Content:



