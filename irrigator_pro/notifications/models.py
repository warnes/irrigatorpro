from django.db import models

from django.contrib.auth.models import User

from common.models import Audit, Comment

from farms.models import CropSeason, Field



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
 
