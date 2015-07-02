#!/usr/bin/env python
from datetime import date, datetime, timedelta
import os, os.path, re, socket, subprocess, sys
import argparse, socket
import psycopg2
import warnings
import ConfigParser
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
from farms.models import ProbeSync, ProbeReading
from django.contrib.auth.models import User
from django.utils import timezone
import pytz


## Current Timezone
eastern = pytz.timezone("US/Eastern")

## Startup Django
django.setup()

###
# Use ConfigParser to pull private values from irrigator_pro.conf
### 
import ConfigParser
config = ConfigParser.ConfigParser()
config.read(os.path.join(ABSOLUTE_PROJECT_ROOT, 
                         "irrigator_pro", 
                         "settings", 
                         "irrigator_pro.conf"))
def unquote(str):
    str = re.sub(r'^\"(.*)\"$', '\\1', str)
    str = re.sub(r'^\'(.*)\'$', '\\1', str)
    return str

## UGA Database Configuration
HOST     = unquote(config.get('UGA Database', 'HOST'))
DATABASE = unquote(config.get('UGA Database', 'DATABASE'))
USER     = unquote(config.get('UGA Database', 'USER'))
PASSWORD = unquote(config.get('UGA Database', 'PASSWORD'))

## User to own probe readings
OWNER='greg@warnes.net'

## Debugging
DEBUG=False

## Global counters
nFiles    = 0
nRecords  = 0
allFiles  = ""

def processProbeReading(record, store_probes=True):
    """
    Extract elements of current record, and store to database if
    between 1am and 9am.

    """

    global nRecords
    global rpr


    ( id,
      datetime,
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
    ) = record;

    if DEBUG:
        print datetime
        sys.stdout.flush()

    user = User.objects.get(email=OWNER)
    now  = timezone.now()

    ## Add local timzone to reading datetime object
    datetime = datetime.replace(tzinfo=timezone.get_current_timezone())
    reading_date = datetime.replace(hour=0, minute=0, second=0, microsecond=0)
    one_day = timedelta(days=1)

    # if _one_ reading for this date already exists, update it
    try:
        rpr = ProbeReading.objects.get(datetime__gte=reading_date,
                                       datetime__lt =reading_date + one_day,
                                       radio_id=radio_id
                                       )
        new_record = False
        sys.stderr.write(".")

    # if _no_ reading exists, create a new one
    except ProbeReading.DoesNotExist:
        rpr = ProbeReading(datetime = datetime,
                           radio_id=radio_id
                           )
        nRecords += 1
        rpr.cuser               = user
        new_record = True
        sys.stderr.write("+")

    # if _more_than_one_ reading exists there is a problem, 
    # so print the offending records. 
    except ProbeReading.MultipleObjectsReturned, e:
        rprs = ProbeReading.objects.filter(datetime__gte=reading_date,
                                           datetime__lt=reading_date + one_day,
                                           radio_id=radio_id)
        print "farm_codes=", map(lambda pr: pr.farm_code, rprs)
        print "probe_codes=", map(lambda pr: pr.farm_code, rprs)
        print "radio_ids=", map(lambda pr: pr.radio_id, rprs)
        print "datetime=", map(lambda pr: pr.datetime, rprs)
        raise e

    rpr.muser               = user

    # Store most recent entry information for everything *except* temperature
    rpr.datetime    = datetime
    rpr.radio_id            = radio_id
    #rpr.file_date           = file_date
    rpr.battery_voltage     = battery_voltage
    rpr.battery_percent     = battery_percent
    rpr.soil_potential_8    = soil_potential_8
    rpr.soil_potential_16   = soil_potential_16
    rpr.soil_potential_24   = soil_potential_24
    rpr.circuit_board_temp  = circuit_board_temp

    rpr.minutes_awake       = minutes_awake
    rpr.muser               = user
    rpr.mdate               = now
    rpr.source              = u'UGADB'

    ## Always store the *highest* temp observed 
    rpr.thermocouple_1_temp = max( rpr.thermocouple_1_temp, thermocouple_1_temp)
    rpr.thermocouple_2_temp = max( rpr.thermocouple_2_temp, thermocouple_2_temp)

    if store_probes:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            rpr.save()

###########################
## Start of main script ###
###########################


## Handle Command Line Arguments
today = date.today()

## Default start date is the last one in the datebase
try:
    date_start_default = ProbeReading.objects.filter(source=u'UGADB').latest('datetime').datetime.date()
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
parser.add_argument('--no-store',
                    action='store_true',
                    help='Do not store probe readings into the database.'
                    ) 
parser.add_argument('--no-log',
                    action='store_true',
                    help='Do not store a log of this execution into the database.'
                    ) 
parser.add_argument('--clean',
                    action='store_true',
                    help='Clean out existing entries in the time range.'
                    ) 


args = parser.parse_args()

store_probes = not args.no_store
store_log    = not args.no_log
store_clean  = args.clean
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

if store_clean:
    pr_query = ProbeReading.objects.filter(datetime__gte=datetime.strptime("%s" % date_start, "%Y-%m-%d"),
                                           datetime__lt=datetime.strptime("%s" % date_end,   "%Y-%m-%d") + timedelta(days=1)
                                           )
    nrecords_before = len(pr_query)
    pr_query.delete()
    pr_query = ProbeReading.objects.filter(datetime__gte=datetime.strptime("%s" % date_start, "%Y-%m-%d"),
                                           datetime__lt=datetime.strptime("%s" % date_end,   "%Y-%m-%d") + timedelta(days=1)
                                           )
    nrecords_after = len(pr_query)
    print "Deleted %d records." % (nrecords_before - nrecords_after)


sys.stderr.write("Progress: (dot=one UGA record processed, plus=new local record created)\n")

## Iterate across records
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


