#!/usr/bin/env python
from datetime import date, datetime, timedelta
import os, os.path, re, socket, subprocess, sys
import argparse, socket
import psycopg2
import warnings
import ConfigParser

"""
This script removes all of the water_register records to force recalculation.
"""

if __name__ == "__main__":
    # Add django root dir to python path
    PROJECT_ROOT      = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',))
    print "PROJECT_ROOT=", PROJECT_ROOT
    sys.path.append(PROJECT_ROOT)


    # Add virtualenv dirs to python path
    host = socket.gethostname()
    print "HOSTNAME=%s" % host
    if host=='irrigatorpro':
        if "test" in PROJECT_ROOT:
            VIRTUAL_ENV_ROOT = '/www/VirtualEnvs/test/'
        elif "devel" in PROJECT_ROOT:
            VIRTUAL_ENV_ROOT = '/www/VirtualEnvs/devel/'
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
from irrigator_pro.settings import ABSOLUTE_PROJECT_ROOT
from farms.models import WaterRegister

# Start up django
django.setup()

print
print
print "Deleting all water register objects...",
WaterRegister.objects.all().delete()
print "Done."
print
print
