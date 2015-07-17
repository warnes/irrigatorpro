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


from datetime import date, datetime
from django.contrib.auth.models import User
from farms.generate_water_register import earliest_register_to_update, generate_water_register, calculateAWC_RainIrrigation
from farms.models import CropSeason, Field, WaterHistory
from farms.utils import get_probe_readings_dict

crop_season = CropSeason.objects.get(name='Corn 2015', description='mine')  # need one with probes.
field = Field.objects.get(name='North')


print 'Performing query'
earliest_date = earliest_register_to_update(date(2015,07,03),
                                            crop_season,
                                            field)

print '############### Earliest to update', earliest_date


print '############### Generating register'

generate_water_register(crop_season,
                        field,
                        User.objects.get(email='aalebl@gmail.com'))


print '############### Testing calculateAWC_RainIrrigation'


probe_readings = get_probe_readings_dict(field, crop_season)
water_history_query = WaterHistory.objects.filter(crop_season=crop_season,
                                                  field=field).all()

(rain, irrigation) = calculateAWC_RainIrrigation(crop_season,
                                                 field,
                                                 date(2015, 06, 30), 
                                                 water_history_query,
                                                 probe_readings)


(rain, irrigation) = calculateAWC_RainIrrigation(crop_season,
                                                 field,
                                                 date(2015, 07, 01), 
                                                 water_history_query,
                                                 probe_readings)


(rain, irrigation) = calculateAWC_RainIrrigation(crop_season,
                                                 field,
                                                 date(2015, 07, 02), 
                                                 water_history_query,
                                                 probe_readings)



