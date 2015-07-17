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


"""
For now only test dictionary creation.
"""
from farms.models import *
from datetime import date, datetime
from django.contrib.auth.models import User

from farms.utils import get_probe_readings_dict

# Get the cumulative report in a given date range. 

user = User.objects.get(email='aalebl@gmail.com')
print "user: ", user

# Get a crop season

crop_season = CropSeason.objects.get(name='Corn 2015', description='mine')  # need one with probes.
field = Field.objects.get(name='North')
print 'crop season: ', crop_season
print 'field: ', field


dict = get_probe_readings_dict(field, crop_season)
print "Dict: ", dict
