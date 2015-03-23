from django.contrib import admin

from common.models import Audit, Comment, Location, NameDesc
from common.admin import AuditAdmin

from notifications.models import *

# Register your models here.

class NotificationsRuleAdmin(AuditAdmin):

    fields = [ 
               'label',
               'get_fields_list',
               'level',
               'notification_type',
               'get_recipients_list',
               'delivery_time',
               'time_zone']

    readonly_fields = fields[1:]

    list_display = ['pk',
                    'label',
                    'get_fields_list',
                    'level',
                    'notification_type',
                    'get_recipients_list',
                    'delivery_time',
                    'time_zone']

    # Make only label editable for not. Need to use control vocabulary for everything else.
    list_editable = ['label'] #, 'delivery_time', 'time_zone']
    
admin.site.register(NotificationsRule, NotificationsRuleAdmin)

