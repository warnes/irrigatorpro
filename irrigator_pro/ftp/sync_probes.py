from ftplib import FTP
from datetime import date, datetime
import re, sys

from farms.models import ProbeSync, RawProbeReading
from django.contrib.auth.models import User
from django.utils import timezone


"""
This script downlaads the UGA SSA data stored on the NESPAL webserver and uploads it into the IrrigatorPro database.
"""

line = "07/25/2013 09:02:07,1,0459FF,2.74,76%,0,0,5.1,23.6,21.4,23.6,1516"

## Configuration
#server   = "170.224.165.20"
#username = "UGA"
#password = "UGA_irrigator"

ftp_server   = "www.nespal.org"
ftp_path     = "/cigflint/flint2013"
ftp_username = "flintcig"
ftp_password = "cigswcd"



nfiles=0
nrecords=0


def putProbe(farm_code, file_date, line):

    global nrecords

    try:
        line = line.decode("utf-8-sig")
    except:
        line = line.decode("utf-8")

    print "\n"
    print "data: %s\n" % line
    print "\n"

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

    reading_date = datetime.strptime(reading_date, "%m/%d/%Y %I:%M:%S")
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

    nrecords += 1

def parse_filename(filename):
    ## Extract farm and date from filename
    (base, ext) = filename.split('.')
    (farm, datestr) = base.split('_')
    month = datestr[0:2]
    day   = datestr[2:4]
    year  = datestr[4:]
    file_date = date(year=int(year), month=int(month), day=int(day))
    #
    return ( filename, farm, file_date )



## Get most recent successful run
ps_query = ProbeSync.objects.filter(success=True)
if ps_query:
    latest_date = ps_query.latest().datetime
else:
    latest_date = datetime(year=2013, month=01, day=01)

## Record this run
user = User.objects.get(username='warnes')
now  = timezone.now()
ps = ProbeSync(datetime=timezone.now(),
               success=False,
               message="Starting sync.",
               nfiles=0,
               nrecords=0,
               filenames="",
               cuser=user,
               cdate=now,
               muser=user,
               mdate=now
              )
ps.save()

## Connect to FTP server
ftp = FTP(host=ftp_server,
          user=ftp_username,
          passwd=ftp_password)

## Change to data directory
ftp.cwd(ftp_path)

## Get list of files and directories
files = ftp.nlst()

# Data directories should match the pattern ##### (5 digits)
dir_pattern = "^[0-9]{5}$"
dir_re = re.compile( dir_pattern )

dirs = filter( lambda x: dir_re.match(x), files)

## Iterate across directories (farms)
for dir in dirs[:2]:
        print "Working on Farm %s " % dir
        sys.stdout.flush()

        ftp.cwd( "/" + ftp_path + "/" + dir + "/" + "daily" )
        files = ftp.nlst()

        filename_farm_date = map(parse_filename, files)
        filename_farm_date = filter(lambda x: x[2] > latest_date.date(), filename_farm_date )
        filenames = map(lambda x: x[0], filename_farm_date)

        ## Iterate across files (days)
        for filename in filenames[:2]:
            nfiles += 1

            print "Working on %s" % filename
            sys.stdout.flush()

            ## Extract farm and date from filename
            (base, ext) = filename.split('.')
            (farm, datestr) = base.split('_')
            month = datestr[0:2]
            day   = datestr[2:4]
            year  = datestr[4:]
            file_date = date(year=int(year), month=int(month), day=int(day))

            print "file_date", file_date
            sys.stdout.flush()

            ftp.retrlines("RETR " + filename,
                          lambda line: putProbe(farm_code=farm, file_date=file_date, line=line)
                         )


ftp.quit()


