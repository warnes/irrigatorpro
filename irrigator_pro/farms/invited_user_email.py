# Class to handle the email sent to invited users.

from irrigator_pro.settings import NOTIFICATION_SMTP, NOTIFICATION_HOST, NOTIFICATION_PORT
import smtplib

import re

from email.mime.text import MIMEText

def send_invitation_email(invited_user, invited_by, farm):

    """ Send an invitation email specifying who is generating the invitation

    
    :param invited_user email of the person receiving the invitation
    :type invited_user python str

    :param invited_by account generating the invitation
    :type invited_by django.contrib.auth.User

    """

    msg = MIMEText(create_message(invited_by, farm))
    msg['Subject'] = "Invitation to join Irrigator Pro"
    msg['from'] = 'admin@irrigatorpro.org'
    msg['to'] = invited_user


    s = smtplib.SMTP(NOTIFICATION_SMTP, NOTIFICATION_PORT)
    print 'sending email'
    s.sendmail('admin@irrigatorpro.org', [invited_user], msg.as_string())
    print 'done'
    s.quit()






def create_message(invited_by, farm):

    """Create the email to be sent.
    :param invited_by user sending the invitation
    :type invited_by django.contrib.auth.User

    :param farm The farm for which the new user is invited
    :type farm farms.models.Farm

    """


    # Extract user name from the unicode string 

    
    message1 =  "Hello\n\n{0}  has invited you to join IrrigatorPro - a web site "\
                "that provides growers with a simple tool to determine when to "\
                "irrigate for optimal crop health - as an authorized user for the "\
                "farm '{1}'.\n\n"\
                "To register for IrrigatorPro, visit\n\n"\
                "    http://irrigatorpro.org/farm/accounts/signup/"\
                "\n\nIf you do not know '{2}', or believe that you have received "\
                "this email in error, simply delete it.\n\n"\
                "If you receive more than one such email, or have "\
                "any question, email us at\n\n" \
                "    webmaster@irrigatorpro.org\n\n"\
                "Sincerely,\n\nThe Irrigator Pro team\n".format(invited_by.__unicode__(), farm.name, invited_by.first_name + " "  + invited_by.last_name)

    return message1;
