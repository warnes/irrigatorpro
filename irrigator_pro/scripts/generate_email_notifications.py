#!/usr/bin/env python

import os, os.path, sys

import socket

def get_emails(notification_rec):

    
    # Use a set instead of list as there could be duplicates.
    ret = []

    for recipient in notification_rec.recipients.all():
        ret.append(recipient.email)
    return ret




# Set up the environment. Copied from sync_probes.py

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



from irrigator_pro.settings import ABSOLUTE_PROJECT_ROOT

from datetime import date, datetime, time
from django.utils import timezone

import pytz
import re

from notifications.models import NotificationsRule
from notifications.notification_email import EmailMessage
from farms.generate_daily_report import daily_report_by_field


## Current Timezone
eastern = pytz.timezone("US/Eastern")

# Get all the active notifications

notifications_query = NotificationsRule.objects.filter(notification_type="Email").exclude(level = "None")
print "# of notifications: ", notifications_query.count()


daily_reports = {}

# Set to doday when done testing
today = date(2014, 07, 03);

p = re.compile('(\d+):(\d+)\s+(\w+)')
for notify in notifications_query:

    # Check that it is the right time: send only in time in notification record is within last 15 minutes
    # Will convert everything to UTC

    workingTimezone = pytz.timezone(notify.time_zone)
    localCurrentTime = datetime.now(workingTimezone)

    m = p.match(notify.delivery_time)

    adjusted_hour = int(m.group(1))
    if m.group(3) == 'pm' and adjusted_hour != 12:
        adjusted_hour = adjusted_hour + 12
    if m.group(3) == 'am' and adjusted_hour == 12:
        adjusted_hour = 0
    
    localNotificationTime = workingTimezone.localize(datetime(localCurrentTime.year,
                                                      localCurrentTime.month,
                                                      localCurrentTime.day,
                                                      adjusted_hour,
                                                      int(m.group(2)),
                                                      0))


    difference = localNotificationTime - localCurrentTime
    if difference.days != -1 or (86399 - difference.seconds) > (60*14):
        print "Would not normally send email, but do it now for testing."
        # continue

    print "Will send email for notification: ", notify.label

    user = notify.cuser
    if user not in daily_reports:
        daily_reports[user] = daily_report_by_field(today, user);
    reports = daily_reports[user];


    email = EmailMessage(get_emails(notify))

    for field in notify.field_list.all():
        if field.pk not in reports: continue
        report = reports[field.pk]
        if ( (notify.level == "Daily")
             or (notify.level == "Any Flag" 
                 and (report.water_register_object.irrigate_flag or
                      report.water_register_object.too_hot_flag or
                      report.water_register_object.check_sensors_flag or
                      report.water_register_object.dry_down_flag))
             or (notify.level == 'Irrigate Today' and report.water_register_object.irrigate_flag)):
            print "Adding for field: ", field
            email.addRecord(report)

        
    email.sendIfNotEmpty()



