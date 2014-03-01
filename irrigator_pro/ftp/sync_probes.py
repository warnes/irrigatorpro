#!/usr/bin/env python
from ftplib import FTP
from datetime import date, datetime
import os, os.path, re, subprocess, sys
import argparse

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
from farms.models import ProbeSync, ProbeReading
from django.contrib.auth.models import User
from django.utils import timezone
import pytz


## Current Timezone
eastern = pytz.timezone("US/Eastern")

## FTP Configuration
ftp_server     = "www.nespal.org"
ftp_path       = "/cigflint/Flint%(year)s" # year will be appended
ftp_email   = "flintcig"
ftp_password   = "cigswcd"
ftp_cache_path = os.path.join(ABSOLUTE_PROJECT_ROOT, "ftp_cache")

print "ftp_cache_path:", ftp_cache_path

## Debugging
DEBUG=False

## Global counters
nFiles    = 0
nRecords  = 0
allFiles  = ""

def mirror(year=2013, max_tries=20):
    """
    Use wget command to mirror the FTP 'daily' files to the local directory 'ftp_cache_path'
    """

    ## Create target directory (if needed)
    try:
        os.mkdir(ftp_cache_path)
    except:
        pass

    os.chdir(ftp_cache_path)

    command = [ 'wget',
                '--mirror',
                '--ftp-user=%s' % ftp_email,
                '--ftp-password=%s' % ftp_password,
                '--exclude-directories=/*/*/*/hourly',
                '--no-verbose',
                '--cut-dirs=6',
                '--tries=%d' % max_tries,
                '--no-host-directories',
                'ftp://%s/%s' % ( ftp_server, ftp_path % {'year': year} )
            ]

    log = subprocess.check_output(command)


def putProbe(farm_code, file_date, line):
    """
    Extract elements of CSV-encoded line, write to database.

    Store last entries before 9:00am on each date.
    """

    global nRecords
    global rpr

    try:
        line = line.decode("utf-8-sig")
    except:
        line = line.decode("utf-8")

    if DEBUG:
        print "data: %s" % line
        sys.stdout.flush()

    ( reading_date,
      probe_code,
      radio_id,
      battery_voltage,
      battery_percent,
      soil_potential_8,
      soil_potential_16,
      soil_potential_32,
      circuit_board_temp,
      thermocouple_1_temp,
      thermocouple_2_temp,
      minutes_awake
    ) = line.split(',')


    reading_date = datetime.strptime("%s EST" % reading_date, "%m/%d/%Y %H:%M:%S %Z")
    try:
        # This can sometimes fail if a particular datetime falls into
        # a daylight-savings transition
        reading_date = timezone.make_aware(reading_date, eastern)
    except pytz.exceptions.AmbiguousTimeError as e:
        print e

    # Only consider times between 1:00am and 9:00am on each date.
    if reading_date.hour < 1 or reading_date.hour > 8:
        return

    if DEBUG:
        print reading_date
        sys.stdout.flush()

    battery_percent = battery_percent.replace("%","")

    user = User.objects.get(email='greg@warnes.net')
    now  = timezone.now()

    # if a reading for this date already exists, update it
    try:
        rpr = ProbeReading.objects.get(farm_code    = farm_code,
                                       reading_date__startswith=reading_date.date(),
                                       probe_code   = probe_code)
    except ProbeReading .DoesNotExist:
        # otherwise create a new one
        rpr = ProbeReading(farm_code    = farm_code,
                           reading_date  = reading_date,
                           probe_code    = probe_code)

        rpr.cuser               = user
        rpr.muser               = user

        nRecords += 1

    rpr.reading_date        = reading_date
    rpr.radio_id            = radio_id
    rpr.file_date           = file_date
    rpr.battery_voltage     = battery_voltage
    rpr.battery_percent     = battery_percent
    rpr.soil_potential_8    = soil_potential_8
    rpr.soil_potential_16   = soil_potential_16
    rpr.soil_potential_32   = soil_potential_32
    rpr.circuit_board_temp  = circuit_board_temp
    rpr.thermocouple_1_temp = thermocouple_1_temp
    rpr.thermocouple_2_temp = thermocouple_2_temp
    rpr.minutes_awake       = minutes_awake
    rpr.muser               = user
    rpr.mdate               = now
    rpr.source              = u'UGADB'

    rpr.save()



def parse_filename(filename):
    """
    Extract farm and date from filename
    """
    (base, ext) = filename.split('.')
    (farm, datestr) = base.split('_')
    month = datestr[0:2]
    day   = datestr[2:4]
    year  = datestr[4:]
    file_date = date(year=int(year), month=int(month), day=int(day), )
    #
    return ( filename, farm, file_date )


###########################
## Start of main script ###
###########################


## Handle Command Line Arguments
today = date.today()
date_start_default = "%s-01-01" % today.year
date_end_default   = today.isoformat(),

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
    
## Synchronize with ftp site
years = range( date_start.year, date_end.year+1 )

if mirror_files:
    for year in years: mirror(year=year)

## Select files to work on
files = os.listdir(ftp_cache_path)
data_files = filter(lambda x: re.match("[0-9]+_[0-9]+\.txt", x), files)
filename_farm_dates = map(parse_filename, data_files)

## Iterate across files
for (filename, farm, file_date) in filename_farm_dates:


    if not (date_start <= file_date <= date_end):
        print "File date '%s' outside range [%s to %s].  Skipped." % \
            ( file_date, date_start, date_end  )
        sys.stdout.flush()
        continue

    # If the file has been fully imported, it will be recorded in a
    # ProbeSync object's filenames field.
    count = ProbeSync.objects.filter( filenames__contains=filename ).count()
    # If it does up, skip it. Otherwise proceed.
    if count > 0:
        print "Farm '%s' for date %s already loaded.  Skipped." % ( farm, file_date )
        sys.stdout.flush()
    else:
        print "Working on farm '%s' for date %s " % ( farm, file_date )
        sys.stdout.flush()

        nFiles += 1
        if allFiles:
            allFiles = allFiles + ", " + filename
        else:
            allFiles = filename

        if store_probes:
            file = open( os.path.join(ftp_cache_path, filename), 'r' )

            for line in file:
                ## add line to database
                putProbe(farm_code=farm, file_date=file_date, line=line)

                if store_log:
                    ## Update ProbeSync record
                    ps.nfiles    = nFiles
                    ps.nrecords  = nRecords
                    ps.filenames = allFiles
                    ps.save()
                    
            file.close()


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


