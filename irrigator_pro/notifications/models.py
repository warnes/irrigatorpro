from django.db import models

from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from common.models import Audit, Comment
from django.db.models import Q

from farms.models import CropSeason, Field, Farm


########################################################
### NotificationsRule
###
### Connect notification info with a Field, CropSeason
########################################################

class NotificationsRule(Comment, Audit):

    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser

    NOTIFICATION_TYPE_VALUES    = ['Email', 'SMS']
    LEVEL_CHOICES               = ['Daily', 'Any Flag', 'Irrigate Today', 'None']

    field_list          = models.ManyToManyField(Field)
    recipients          = models.ManyToManyField(User)

    level               = models.CharField(max_length = 15)
    notification_type   = models.CharField(max_length = 15)

    label               = models.CharField(max_length = 50)

    # Will use format "hh:mm" to save the time
    delivery_time       = models.CharField(max_length = 10)
    time_zone           = models.CharField(max_length = 50)


    # Next two are used in admin interface

    def get_fields_list(self):
        f = self.field_list.all()
        return ', '.join([ obj.name for obj in f])

    def get_recipients_list(self):
        r = self.recipients.all()
        return ', '.join([ obj.email for obj in r])

    def recipients_changed(sender, **kwargs):
        # Must be an easier way, but this will work for now
        if kwargs.get('action') != "post_add": return
        farm = kwargs.get('instance', None)
        farm_users = farm.get_farmer_and_user_objects()

        for notify in NotificationsRule.objects.all():  # Here should filter by checking farm in first field. .filter(Q(field_list__[0].farm = sender)):
            if len( notify.field_list.all() ) > 0:
                aField = notify.field_list.all()[0]
                if aField.farm != farm: continue
                for recipient in notify.recipients.all():
                    if recipient not in farm_users:
                        notify.recipients.remove(recipient)
                    notify.save()

    def __init__(self, *args, **kwargs):
        super(NotificationsRule, self).__init__(*args, **kwargs)
        self.attached_fields = []
    

    # Set up for receiving signal when the users list has changed
    m2m_changed.connect(recipients_changed, sender = Farm.users.through)

    class Meta:
        verbose_name = "Notification Rule"
