#!/usr/bin/env python
from ftplib import FTP
from datetime import date, datetime
import os, os.path, re, subprocess, sys
import argparse, socket
import psycopg2
import warnings

"""
This script queries the UGA SSA data stored in the NESPAL database and
upload the last probe reading before 9am per day for each probe into
the IrrigatorPro database.
"""

if __name__ == "__main__":
    # Add django root dir to python path
    PROJECT_ROOT      = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',))
    print "PROJECT_ROOT=", PROJECT_ROOT
    sys.path.append(PROJECT_ROOT)

    # Add virtualenv dirs to python path
    if socket.gethostname()=='gregs-mbp':
        VIRTUAL_ENV_ROOT = os.path.join( PROJECT_ROOT, 'VirtualEnvs', 'irrigator_pro')
    else:
        VIRTUAL_ENV_ROOT = '/prod/VirtualEnvs/irrigator_pro/'

    print "VIRTUAL_ENV_ROOT='%s'" % VIRTUAL_ENV_ROOT
    activate_this = os.path.join(VIRTUAL_ENV_ROOT, 'bin', 'activate_this.py')
    execfile(activate_this, dict(__file__=activate_this))

    # Get settings
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "irrigator_pro.settings")

from irrigator_pro.settings import ABSOLUTE_PROJECT_ROOT
from farms.models import ProbeSync, ProbeReading
from django.contrib.auth.models import User
from django.utils import timezone
import pytz


## Current Timezone
eastern = pytz.timezone("US/Eastern")

## UGA Database Configuration
HOST="162.243.88.127"
DATABASE="flint"
USER="reader"
PASSWORD="ugatifton"

## User to own probe readings
OWNER='greg@warnes.net'

## Debugging
DEBUG=False

## Global counters
nFiles    = 0
nRecords  = 0
allFiles  = ""

def processProbeReading(fields, store_probes=True):
    """
    Write elements of current line and write to database.

    Store last entry before 9:00am on each date.
    """

    global nRecords
    global rpr


    ( id,
      reading_datetime,
      farm_code,
      probe_code,
      radio_id,
      battery_voltage,
      battery_percent,
      soil_potential_8,
      soil_potential_16,
      soil_potential_24,
      circuit_board_temp,
      thermocouple_1_temp,
      thermocouple_2_temp,
      minutes_awake
    ) = fields;

    # Only consider times between 1:00am and 9:00am on each date.
    if (reading_datetime.hour < 1) or (reading_datetime.hour > 8):
        return

    if DEBUG:
        print reading_datetime
        sys.stdout.flush()

    user = User.objects.get(email=OWNER)
    now  = timezone.now()

    # if a reading for this date already exists, update it
    try:
        rpr = ProbeReading.objects.get(farm_code    = farm_code,
                                       reading_datetime__startswith=reading_datetime.date(),
                                       probe_code   = probe_code)
    except ProbeReading .DoesNotExist:
        # otherwise create a new one
        rpr = ProbeReading(farm_code    = farm_code,
                           reading_datetime  = reading_datetime,
                           probe_code    = probe_code)

        rpr.cuser               = user
        rpr.muser               = user

        nRecords += 1

    rpr.reading_datetime    = reading_datetime
    rpr.radio_id            = radio_id
    #rpr.file_date           = file_date
    rpr.battery_voltage     = battery_voltage
    rpr.battery_percent     = battery_percent
    rpr.soil_potential_8    = soil_potential_8
    rpr.soil_potential_16   = soil_potential_16
    rpr.soil_potential_24   = soil_potential_24
    rpr.circuit_board_temp  = circuit_board_temp
    rpr.thermocouple_1_temp = thermocouple_1_temp
    rpr.thermocouple_2_temp = thermocouple_2_temp
    rpr.minutes_awake       = minutes_awake
    rpr.muser               = user
    rpr.mdate               = now
    rpr.source              = u'UGADB'

    if store_probes:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            rpr.save()
    
    sys.stderr.write(".")


###########################
## Start of main script ###
###########################


## Handle Command Line Arguments
today = date.today()

## Default start date is the last one in the datebase
try:
    date_start_default = ProbeReading.objects.filter(source=u'UGADB').latest('reading_datetime').reading_datetime.date()
except:
    date_start_default = "%s-01-01" % today.year

## Default end date is today
date_end_default   = today.isoformat(),

## Parse Arguments
parser = argparse.ArgumentParser(description='Download probe readings and import into database')
parser.add_argument('--date-start',
                    action='store',
                    default=date_start_default,
                    help="Earliest probe reading date to process, in yyyy-mm-dd format - Default is %s" % date_start_default)
parser.add_argument('--date-end',
                    action='store',
                    default=date_end_default,
                    help="Latest probe reading date to process, in yyyy-mm-ddd format - Default is %s" % date_end_default)
parser.add_argument('--no-files',
                    action='store_true',
                    help='Do not update local copy of server files.'
                    ) 
parser.add_argument('--no-store',
                    action='store_true',
                    help='Do not store probe readings into the database.'
                    ) 
parser.add_argument('--no-log',
                    action='store_true',
                    help='Do not store a log of this execution into the database.'
                    ) 

args = parser.parse_args()

mirror_files = not args.no_files
store_probes = not args.no_store
store_log    = not args.no_log
date_start   = datetime.strptime("%s EST" % args.date_start, "%Y-%m-%d %Z").date()
date_end     = datetime.strptime("%s EST" % args.date_end, "%Y-%m-%d %Z").date()

## Store a record of this run

if store_log:
    ## Record the start of this run in the ProbeSync table
    user = User.objects.get(email='greg@warnes.net')
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

## Connect with the UGA database
conn = psycopg2.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD) 
cur = conn.cursor()
SQL='''
    SELECT * 
    FROM flint.fields.data 
    WHERE 
      date_trunc('day', dt) >= TIMESTAMP '%s'
      AND
      date_trunc('day', dt) <= TIMESTAMP '%s'
    ''' % ( date_start, date_end ) 

cur.execute( SQL )

sys.stderr.write("Synchronizing probe information via direct database access\n")
sys.stderr.write("\n")
sys.stderr.write("Date range: %s to %s \n" % ( date_start, date_end ) )
sys.stderr.write("\n")
sys.stderr.write("Progress: (one dot per record)\n")

## Iterate across files
for record in cur:

   ## add line to database
   processProbeReading(record, store_probes=store_probes)

   if store_log:
       ## Update ProbeSync record
       ps.nrecords  = nRecords
       ps.save()

sys.stderr.write("\n\n")

cur.close()
conn.close()
    
## Finalize ProbeSync record
if store_log:
    ps.success   = True
    ps.message   = "Successful sync of dates from %s to present"
    ps.nfiles    = nFiles
    ps.nrecords  = nRecords
    ps.filenames = allFiles
    ps.muser     = user
    ps.mdate     = timezone.now()
    ps.save()


