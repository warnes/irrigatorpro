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

from farms.generate_cumulative_report import generate_cumulative_report
from farms.models import CropSeason, Field
from datetime import date, datetime
from django.contrib.auth.models import User

# Get the cumulative report in a given date range. 

user = User.objects.get(email='aalebl@gmail.com')
print "user: ", user


reports = generate_cumulative_report(date(2014, 2, 8), date(2014, 7, 31), user)
for r in reports:
    print r.farm
    print r.field
    print r.crop
    print r.start_date
    print r.end_date
    print r.cumulative_rain
    print r.cumulative_irrigation_vol
    print r.cumulative_water_use
    print r.days_of_irrigation

    print "\n\n"


