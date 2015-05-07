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



from twilio.rest import TwilioRestClient

# Your Account Sid and Auth Token from twilio.com/user/account

account_sid = "AC642f7826a30e9666db2716553adf4461"
auth_token = "38e7c453fee0d95d852af80483025ae2"
client = TwilioRestClient(account_sid, auth_token)
message = client.messages.create(body="Test frompython api",
to="+1XXXXXXX", # Replace with your phone number
from_="+15856729419") # Replace with your Twilio number
print message.sid
