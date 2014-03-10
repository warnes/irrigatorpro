#!/usr/bin/env python
import os, os.path, re, subprocess, sys
import argparse
import datetime
import math

"""
This script downlaads the UGA SSA data stored on the NESPAL webserver and uploads it into the IrrigatorPro database.
"""

if __name__ == "__main__":
    # Add the directory *above* this to the python path so we can find our modules
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "irrigator_pro.settings")
else: # assume we're running in the script directory
    sys.path.append("..")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "irrigator_pro.settings")


from irrigator_pro.settings import ABSOLUTE_PROJECT_ROOT
from farms.models import *
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured

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
    #try:
    if 1:
        print "Query...",
        crop_season = CropSeason.objects.filter(field_list=field,
                                                season_start_date__gte=date).order_by("-season_start_date")#.first()
        print "crop_season=", crop_season
        #!FIXME: So season-end date is available, so this doesn't
        #!prevent incorrect matching against a previous crop season if
        #!this filed is not included in a later one.
        print "Query...",
        crop = crop_season.crop
        print "crop=", crop
        max_root_depth = CropSeason.crop.max_root_depth
        print "max_root_depth=", max_root_depth
    #except:
    #    return None


    ## Find any probe readings for date with this radio_id
    probe_reading = ProbeReading.objects.filter(radio_id=radio_id,
                                                reading_datetime__startswith=date).order_by('reading_datetime').last()

    if not probe_reading:
        return None

    soil_type_parameters = SoilTypeParameter.objects.filter(soil_type=field.soil_type)

    try:
        soil_type_8in  = soil_type_parameters.get(depth=8 )
    except ObjectDoesNotExist:
        raise ImproperlyConfigured("Missing parameters for soiltype '%s': %d inch depth missing" % ( field.soil_type, 8) )

    try:
        soil_type_16in = soil_type_parameters.get(depth=16)
    except ObjectDoesNotExist:
        raise ImproperlyConfigured("Missing parameters for soiltype '%s': %d inch depth missing" % ( field.soil_type, 16) )

    try:
        soil_type_24in = soil_type_parameters.get(depth=24)
    except ObjectDoesNotExist:
        raise ImproperlyConfigured("Missing parameters for soiltype '%s': %d inch depth missing" % ( field.soil_type, 24) )


    # IF(O48="","",IF(O48=0,$H$5,IF(((R$3+R$4*LN(O48))-(R$3+R$4*LN(40)))*24>$H$5,$H$5,((R$3+R$4*LN(O48))-(R$3+R$4*LN(40)))*24)))
    #
    # O48  = probe_reading.soil_potential_8
    # H$5$ = field.soil_type.max_available_water
    # R$3  = soil_type_8in.intercept
    # R$4  = soil_type_8in.slope
    #
    # IF(O48="","",
    #    IF(O48=0,
    #       $H$5,
    #       IF(
    #               (
    #                   (R$3+R$4*LN(O48))-(R$3+R$4*LN(40))
    #               )*24>$H$5,
    #               $H$5,
    #               (
    #                   (R$3+R$4*LN(O48))-(R$3+R$4*LN(40))
    #               )*24
    #       )
    #   )
    # )

    # =IF(O48="","",IF(O48=0,$H$5,IF(((R$3+R$4*LN(O48))-(R$3+R$4*LN(40)))*24>$H$5,$H$5,((R$3+R$4*LN(O48))-(R$3+R$4*LN(40)))*24)))
    # =IF(P48="","",IF(P48=0,$H$5,IF(((S$3+S$4*LN(P48))-(S$3+S$4*LN(40)))*24>$H$5,$H$5,((S$3+S$4*LN(P48))-(S$3+S$4*LN(40)))*24)))
    # =IF(Q48="","",IF(Q48=0,$H$5,IF(((T$3+T$4*LN(Q48))-(T$3+T$4*LN(40)))*24>$H$5,$H$5,((T$3+T$4*LN(Q48))-(T$3+T$4*LN(40)))*24)))

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


    AWC = (AWC_8 + AWC_16 + AWC_24)/3

    #print 'Mean AWC=%4.2f' % AWC

    if AWC > field.soil_type.max_available_water:
        AWC = field.soil_type.max_available_water

    return AWC


if __name__ == "__main__":
    farm = Farm.objects.get(pk=1)
    field = Field.objects.filter(farm=farm)[0]

    for day_of_month in range(1,31):
        date = datetime.date(2013, 4, day_of_month)
        print "Calculating AWC for date: %s" % date,
        AWC = calculateAWC_ProbeReading(field, date)
        print "=", AWC

























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



