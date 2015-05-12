#!/usr/bin/env python

""" Test program for invited user
This program will test the conversion of a user from invited to real user.
"""

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
from farms.models import Farm, InvitedUser
from contact_info.models import Contact_Info

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist



###
## Method to clean up. Can be called at beginning to remove remnants of previous runs,
## of at the end to remove newly created entries in db.
##

def cleanup(email):

    for u in InvitedUser.objects.all():
        u.delete()

    try:
        u = User.objects.get(email = email)
        u.delete()
    except ObjectDoesNotExist:
        pass
        

    




user = User.objects.get(email='aalebl@gmail.com')


# Create a couple of farms
(farm1, created) = Farm.objects.get_or_create(name="test_farm_1",
                                              farmer = user,
                                              defaults = { 'cuser': user,
                                                           'muser': user,
                                                    }
                                          )

(farm2, created) = Farm.objects.get_or_create(name="test_farm_2",
                                              farmer = user,
                                              defaults = { 'cuser': user,
                                                           'muser': user,
                                                    }
                                          )


# Create an invited user
email = "XXXX@xxxxx.com"
cleanup(email)
invited_user = InvitedUser(email=email, cuser_id = user.id, muser_id = user.id)
invited_user.save()


# Add both farms to this invited user

invited_user.farms.add(farm1)
invited_user.farms.add(farm2)

# Create a user record from invited_user

new_user = User(email=email)
new_user.save()

contact_info = Contact_Info(user=new_user, cuser = new_user, muser = new_user)
contact_info.save()




# Cleanup everything

#farm1.delete()
#farm2.delete()



