#!/usr/bin/env python

import os, os.path, sys
import socket

if __name__ == "__main__":
    PROJECT_ROOT      = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',))
    print "PROJECT_ROOT=", PROJECT_ROOT
    sys.path.append(PROJECT_ROOT)


    # Add virtualenv dirs to python path
    host = socket.gethostname()
    print "HOSTNAME=%s" % host


    if host=='irrigatorpro':
        if "test" in PROJECT_ROOT:
            VIRTUAL_ENV_ROOT = '/www/VirtualEnvs/test/'
        else:
            VIRTUAL_ENV_ROOT = '/www/VirtualEnvs/irrigator_pro/'
    else:
        VIRTUAL_ENV_ROOT = os.path.join( PROJECT_ROOT, 'VirtualEnvs', 'irrigator_pro')

    print "VIRTUAL_ENV_ROOT='%s'" % VIRTUAL_ENV_ROOT

    activate_this = os.path.join(VIRTUAL_ENV_ROOT, 'bin', 'activate_this.py')
    execfile(activate_this, dict(__file__=activate_this))

    # Get settings
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "irrigator_pro.settings")


import django
django.setup()

from farms.unified_field_data import generate_objects

from farms.models import *
from datetime import date, datetime
from django.contrib.auth.models import User

# Get the cumulative report in a given date range. 

user = User.objects.get(email='aalebl@gmail.com')
print "user: ", user

# Get a crop season

crop_season = CropSeason.objects.get(pk=19)  # need one with probes.
field = Field.objects.get(pk=33)
print 'crop season: ', crop_season
print 'field: ', field

unified_records = generate_objects(crop_season, field, user, date.today())

for r in unified_records:
    print r.date
    print r.water_register

    print r.uga_records

    print r.manual_records
