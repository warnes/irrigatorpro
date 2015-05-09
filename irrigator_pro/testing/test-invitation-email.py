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

from django.contrib.auth.models import User
import django
django.setup()

from farms.invited_user_email import send_invitation_email
from farms.models import Farm

user = User.objects.get(email='aalebl@gmail.com')
farm = Farm.objects.get(name="HHERC")

send_invitation_email("aalebl@gmail.com", user, farm)
send_invitation_email("alainxyzleblanc@aol.com", user, farm)
send_invitation_email("alainleblanc@yahoo.com", user, farm)
send_invitation_email("greg@warnes.net", user, farm)
