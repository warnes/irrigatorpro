#!/usr/bin/env python
from datetime import date, datetime, timedelta
import os, os.path, re, socket, subprocess, sys
import argparse, socket
import psycopg2
import warnings
import ConfigParser
"""
This script queries the UGA SSA data stored in the NESPAL database
pull relevant probe summary data into the WaterHistory table.
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
import pytz
from irrigator_pro.settings import ABSOLUTE_PROJECT_ROOT
from farms.models import ProbeSync
from django.contrib.auth.models import User
from django.utils import timezone
from farms.generate_water_register import generate_water_register

## Current Timezone
eastern = pytz.timezone("US/Eastern")

## Startup Django
django.setup()
from uga.pull_probes import *

## Debugging
DEBUG=False

###########################
## Start of main script ###
###########################

## get or create sync user
user = User.objects.filter(username='SyncProcess').first()
if user is None:
    user = User.objects.create_user(username='SyncProcess',
                                    email='webmaster@irrigatorpro.org')

## Handle Command Line Arguments
today = timezone.now()

## By default, synchronize current CropSeasons
date_start_default = today

## Default end date is today
date_end_default   = today

## Parse Arguments
parser = argparse.ArgumentParser(description='Download probe readings and import into database, then recompute affected water register records')
parser.add_argument('--date-start',
                    action='store',
                    default=None,
                    help="Earliest crop season to process, in yyyy-mm-dd format - Default is today.")
parser.add_argument('--date-end',
                    action='store',
                    default=None,
                    help="Latest crop season date to process, in yyyy-mm-ddd format - Default is today.")
parser.add_argument('--no-log',
                    action='store_true',
                    help='Do not store a log of this execution into the database.'
                    ) 
parser.add_argument('--clean',
                    action='store_true',
                    help='Clean out existing entries in the time range.'
                    ) 
parser.add_argument('--all',
                   action='store_true',
                   help='Process all available crop seasons from 2013-01-01 forward.'
                   )
parser.add_argument('--no-recompute',
                    action='store_true',
                    help='Do not recompute water register records affected by updates.'
                    )


args = parser.parse_args()

store_log    = not args.no_log
store_clean  = args.clean
if args.date_start: 
    date_start   = datetime.strptime("%s EST" % args.date_start, "%Y-%m-%d %Z")
else:
    date_start   = date_start_default

if args.date_end:
    date_end     = datetime.strptime("%s EST" % args.date_end, "%Y-%m-%d %Z")
else:
    date_end     = date_end_default

if args.all:
    date_start = datetime.strptime("2011-01-01 EST", "%Y-%m-%d %Z")
    date_end   = today

def to_tz_date(datetime):
    if timezone.is_aware(datetime):
        return datetime.date()
    else:
        return timezone.make_aware( datetime, timezone.get_default_timezone() ).date()

date_start = to_tz_date(date_start)
date_end   = to_tz_date(date_end)


## Store a record of this run

if store_log:
    ## Record the start of this run in the ProbeSync table
    now  = timezone.now()
    ps = ProbeSync(datetime  = timezone.now(),
                   success   = False,
                   message   = "Starting sync.",
                   nfiles    = 0,
                   nrecords  = 0,
                   filenames = "",
                   cuser     = user,
                   cdate     = now,
                   muser     = user,
                   mdate     = now
                  )
    ps.save()

sys.stderr.write("\n")
sys.stderr.write("Synchronizing probe information via direct database access\n")
sys.stderr.write("for crop seasons active between %s and %s. \n" % ( date_start, date_end ) )
sys.stderr.write("\n")

if store_clean:
    pr_query = WaterHistory.objects.filter(source='UGA',
                                           datetime__gte=datetime.strptime("%s" % date_start, "%Y-%m-%d"),
                                           datetime__lt=datetime.strptime("%s" % date_end,   "%Y-%m-%d") + timedelta(days=1)
                                           )
    nrecords_before = len(pr_query)
    pr_query.delete()
    pr_query = WaterHistory.objects.filter(source='UGA',
                                           datetime__gte=datetime.strptime("%s" % date_start, "%Y-%m-%d"),
                                           datetime__lt=datetime.strptime("%s" % date_end,   "%Y-%m-%d") + timedelta(days=1)
                                           )
    nrecords_after = len(pr_query)
    print "Deleted %d records." % (nrecords_before - nrecords_after)


start_time = timezone.now()
records = pull_probes_by_period( date_start, date_end )
elapsed = timezone.now() - start_time

nRecords = len(records)

if store_log:
    ## Update ProbeSync record
    ps.nrecords  = nRecords
    ps.save()


## Finalize ProbeSync record
if store_log:
    ps.success   = True
    ps.message   = "Successful sync for cropseasons active between %s and %s" % (date_start, date_end)
    ps.nfiles    = 0
    ps.nrecords  = nRecords
    ps.filenames = ''
    ps.muser     = user
    ps.mdate     = timezone.now()
    ps.save()

print "%d WaterRegister records created/updated in %f seconds." % (nRecords, elapsed.total_seconds())
sys.stderr.write("\n\n")

print
print "Updating water register records..."
print
nChanged = 0
for crop_season in CropSeason.objects.all():
    for field in crop_season.field_list.all():
        nChanged += generate_water_register(crop_season,
                                            field,
                                            User.objects.get(email='aalebl@gmail.com'))
print
print "%d water register records updated." % nChanged
print
print
