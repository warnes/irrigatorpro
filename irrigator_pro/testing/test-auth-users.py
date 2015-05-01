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

from farms.auth_users_processing import extract_email, AuthUserException, add_users
from farms.models import Farm

print extract_email('Leblanc, alain (aalebl@gmail.com)  ')
print extract_email('aalebl@gmail.com')

try:
    extract_email('aalebl@gmail')
    print 'Missed exception.'
except AuthUserException:
    print 'Caught exception ok'

new_users = ['alainleblanc@yahoo.com', 'isidore@laferme.ca']
farm = Farm.objects.get(pk=20)

add_users(farm, new_users)





