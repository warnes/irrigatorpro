# Class to handle the email sent to invited users.

from irrigator_pro.settings import NOTIFICATION_SMTP, NOTIFICATION_HOST, NOTIFICATION_PORT
import smtplib

from email.mime.text import MIMEText

def send_invitation_email(invited_user, invited_by):

    """ Send an invitation email specifying who is generating the invitation

    
    :param invited_user email of the person receiving the invitation
    :type invited_user python str

    :param invited_by account generating the invitation
    :type invited_by django.contrib.auth.User

    """

    msg = MIMEText(create_message(invited_by))
    msg['Subject'] = "Invitation to join Irrigator Pro"
    msg['from'] = 'admin@irrigatorpro.org'
    msg['to'] = invited_user


    s = smtplib.SMTP(NOTIFICATION_SMTP, NOTIFICATION_PORT)
    print 'sending email'
    s.sendmail('admin@irrigatorpro.org', [invited_user], msg.as_string())
    print 'done'
    s.quit()






def create_message(invited_by):

    message1 = "You are receiving this email because a Irrigator Pro user has added your " \
    "email to the list of authorized users for one of his farms. The user information " \
    "from the website is:\n\n    {0}\n\n" \
    "If you do not recognize this user information, or believe that you have " \
    "received this email in error, you can simply delete it. If you receive more " \
    "than one such email, or have any question, you can email us at\n\n" \
    "    admin@irrigatorpro.org\n\n" \
    "If you wish to create an account with Irrigator Pro, you can do so at\n\n" \
    "    http://irrigatorpro.org/farm/accounts/signup/\n\n" \
    "Sincerely\nThe Irrigator Pro team.".format(invited_by.__unicode__())

    return message1;
