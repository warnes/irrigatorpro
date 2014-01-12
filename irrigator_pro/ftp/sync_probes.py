#!/usr/bin/env python
from ftplib import FTP
from datetime import date, datetime
import os, os.path, re, subprocess, sys

"""
This script downlaads the UGA SSA data stored on the NESPAL webserver and uploads it into the IrrigatorPro database.
"""

if __name__ == "__main__":
    # Add the directory *above* this to the python path so we can find our modules
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "irrigator_pro.settings")

from irrigator_pro.settings import BASE_DIR
from farms.models import ProbeSync, RawProbeReading
from django.contrib.auth.models import User
from django.utils import timezone
import pytz


## Current Timezone
eastern = pytz.timezone("US/Eastern")

## FTP Configuration
ftp_server     = "www.nespal.org"
ftp_path       = "/cigflint/Flint2013"
ftp_username   = "flintcig"
ftp_password   = "cigswcd"
ftp_cache_path = os.path.join(BASE_DIR, "ftp_cache")

## Debugging
DEBUG=False

## Global counters
nFiles    = 0
nRecords  = 0
allFiles  = ""

def mirror(max_tries=20):
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
                '--ftp-user=%s' % ftp_username,
                '--ftp-password=%s' % ftp_password,
                '--exclude-directories=/*/*/*/hourly',
                '--no-verbose',
                '--cut-dirs=6',
                '--tries=%d' % max_tries,
                '--no-host-directories',
                'ftp://%s/%s' % ( ftp_server, ftp_path )
            ]

    log = subprocess.check_output(command)


def putProbe(farm_code, file_date, line):
    """
    Extract elements of CSV-encoded line, write to database
    """

    global nRecords

    try:
        line = line.decode("utf-8-sig")
    except:
        line = line.decode("utf-8")

    if DEBUG:
        print "data: %s" % line
        sys.stdout.flush()

    ( reading_date,
      node_id,
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

    reading_date = timezone.make_aware(datetime.strptime("%s EST" % reading_date, "%m/%d/%Y %H:%M:%S %Z"), eastern)

    if DEBUG:
        print reading_date
        sys.stdout.flush()

    battery_percent = battery_percent.replace("%","")

    user = User.objects.get(username='warnes')
    now  = timezone.now()

    rpr = RawProbeReading(farm_code           = farm_code,
                          file_date           = file_date,
                          reading_date        = reading_date,
                          node_id             = node_id,
                          radio_id            = radio_id,
                          battery_voltage     = battery_voltage,
                          battery_percent     = battery_percent,
                          soil_potential_8    = soil_potential_8,
                          soil_potential_16   = soil_potential_16,
                          soil_potential_32   = soil_potential_32,
                          circuit_board_temp  = circuit_board_temp,
                          thermocouple_1_temp = thermocouple_1_temp,
                          thermocouple_2_temp = thermocouple_2_temp,
                          minutes_awake       = minutes_awake,
                          cuser=user,
                          cdate=now,
                          muser=user,
                          mdate=now
                          )
    rpr.save()

    nRecords += 1


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

## Record the start of this run in the ProbeSync table
user = User.objects.get(username='warnes')
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
mirror()

## Select files to work on
files = os.listdir(ftp_cache_path)
data_files = filter(lambda x: re.match("[0-9]+_[0-9]+\.txt", x), files)
filename_farm_dates = map(parse_filename, data_files)

## Iterate across files
for (filename, farm, file_date) in filename_farm_dates:

    print "Working on farm '%s' for date %s " % ( farm, file_date )
    sys.stdout.flush()

    count = RawProbeReading.objects.filter( farm_code=farm, file_date=file_date ).count()

    # check if this data has already been imported
    if count > 0: next

    nFiles += 1
    if allFiles:
        allFiles = allFiles + ", " + filename
    else:
        allFiles = filename


    file = open( filename, 'r' )

    for line in file:
        ## add line to database
        putProbe(farm_code=farm, file_date=file_date, line=line)

        ## Update ProbeSync record
        ps.nfiles    = nFiles
        ps.nrecords  = nRecords
        ps.filenames = allFiles
        ps.save()

    file.close()


## Finalize ProbeSync record
ps.success   = True
ps.message   = "Successful sync of dates from %s to present"
ps.nfiles    = nFiles
ps.nrecords  = nRecords
ps.filenames = allFiles
ps.muser     = user
ps.mdate     = timezone.now()
ps.save()


