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

    NOTIFICATION_TYPE_VALUES    = ['SMS', 'Email']
    LEVEL_CHOICES               = ['Urgent', '7 Days', 'Daily']

    field_list          = models.ManyToManyField(Field)
    recipients          = models.ManyToManyField(User)

    level               = models.CharField(max_length = 15)
    notification_type   = models.CharField(max_length = 15)


    
