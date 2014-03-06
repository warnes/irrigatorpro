#!/usr/bin/env python
import os, os.path, re, subprocess, sys
import argparse
import datetime

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

    ## Find any probe readings for date with this radio_id
    probe_reading = ProbeReading.objects.filter( radio_id=radio_id, reading_datetime__startswith=date).order_by('reading_datetime').last()

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


    AWC_8  = soil_type_8in.intercept  + soil_type_8in.slope  * float(probe_reading.soil_potential_8 )
    AWC_16 = soil_type_16in.intercept + soil_type_16in.slope * float(probe_reading.soil_potential_16)
    AWC_24 = soil_type_24in.intercept + soil_type_24in.slope * float(probe_reading.soil_potential_24)
    AWC = AWC_8 + AWC_16 + AWC_24

    return AWC


if __name__ == "__main__":
    farm = Farm.objects.get(pk=1)
    field = Field.objects.filter(farm=farm)[0]

    date = datetime.date(2013, 4, 16)
    print "Test1: Calculating AWC for date: %s" % date,
    AWC = calculateAWC_ProbeReading(field, date)
    print "=", AWC

    date = datetime.date(2013, 4, 18)
    print "Test1: Calculating AWC for date: %s" % date,
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



