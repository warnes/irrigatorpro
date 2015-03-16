from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.db.models import Q
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User


from django.http import HttpResponseRedirect

from datetime import date, datetime

from notifications.models import NotificationsRule, Field

from farms.models import CropSeason, Farm, Field

from pytz import common_timezones

import re

def farms_filter(user):
    return Farm.objects.filter( Q(farmer=user) |
                                Q(users=user) ).distinct()

# Return an list of times in 15 minutes increments
def get_available_times():

    ret = []
    for am_pm in ['am', 'pm']:
        for hour in [12] + ( range(1, 12)):
            for minutes in ['00', '15', '30', '45']:
                x =  str(hour) + ":" +  minutes + " "+ am_pm
                ret.append(ValidID(x))
    return ret


# Return list of timezones. Will remove some we know are wnot needed (Antarctica?)
def get_available_timezones():
    filtered_list = [ValidID(i) for i in common_timezones if (i.find('Africa') != 0)]
    return filtered_list 


def get_available_levels():
    ret = []
    for x in NotificationsRule.LEVEL_CHOICES:
        ret.append(ValidID(x))
    return ret



# Could probably use the ListView since we only need the notification 
# objects for the current crop_season
class NotificationsSetupView(TemplateView):

    template_name = "notifications/notifications_setup_list.html"


    # Get method is used when loading original page, deleting a row
    def get(self, request, *args, **kwargs):
        if request.GET.get('delete_row') is  not None:
            obj = NotificationsRule.objects.get(pk = request.GET.get('delete_row'))
            obj.delete()

        return render(request, self.template_name, self.get_context_data())


    # Post method is used when adding or editing a row
    def post(self, request, *args, **kwargs):

        pk = request.POST["pk"]
        if (pk == "-1"):
            notifications = NotificationsRule()
        else:
            notifications = NotificationsRule.objects.get(pk = pk)
            notifications.recipients.clear()
            notifications.field_list.clear()

        

        notifications.save()
        
        for x in request.POST.getlist("select-fields"):
            notifications.field_list.add(Field.objects.get(pk=x))

        notifications.notification_type = request.POST.get('communication-type')
        notifications.level = request.POST.get('alert-level')
        notifications.label = request.POST.get('label')
        notifications.delivery_time = request.POST.get('notification-time')
        notifications.time_zone = request.POST.get('timezone')

        for x in request.POST.getlist("select-users"):
            notifications.recipients.add(User.objects.get(pk=x))

        

        notifications.save();
        return HttpResponseRedirect(reverse('notifications'))  # back to the same page


    # Get all the notifications for this user and any crop season not yet
    # ended. Will include crop seasons not yet started.

    def get_notifications_list(self):
            
        notifications_rule_list = NotificationsRule.objects.all() #.filter(Q(crop_season__season_end_date__gte = self.today_date)).all
        return notifications_rule_list


    def get_farm_fields(self):
        farm_fields = {}
        for farm in farms_filter(self.request.user):
            fields = []
            for field in farm.get_fields():
                fields.append(field)
            farm_fields[farm] = fields

        return farm_fields



    def get_farm_users(self):
        farm_users = {}
        for farm in farms_filter(self.request.user):
            users = []
            for user in farm.get_farmer_and_user_objects():
                users.append(user)
            farm_users[farm] = users

        return farm_users





    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # There are either parameters for year, month, day, or none.
        year_param = kwargs.get('year', None)
        self.year = None
        if year_param is not None:
            self.year = int(year_param)
            self.month= int(kwargs.get('month', None))
            self.day = int(kwargs.get('day', None))

        self.today_date = date.today()
        if self.year is not None:
            self.today_date = date(self.year, self.month, self.day)

        return super(NotificationsSetupView, self).dispatch(*args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super(NotificationsSetupView, self).get_context_data(**kwargs)
        context['notifications_list']   = self.get_notifications_list()
        context['farms']                = farms_filter(self.request.user)
        context['farm_fields']          = self.get_farm_fields()
        context['farm_users']           = self.get_farm_users()
        context['notifications_types']  = NotificationsRule.NOTIFICATION_TYPE_VALUES
        context['alert_levels']         = get_available_levels
        context['available_times']      = get_available_times
        context['available_timezones']  = get_available_timezones
        return context



# May want to move somewhere else. May need again.

class ValidID:

    def __init__(self, value):

        self.value = value
        self.id = re.sub('\W', "_", value)
