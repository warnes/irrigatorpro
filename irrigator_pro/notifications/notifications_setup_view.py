from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.db.models import Q
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User

from django.http import HttpResponse, HttpResponseRedirect

from datetime import date, datetime

from notifications.models import NotificationsRule, Field

from farms.models import Farm, Field

from pytz import common_timezones

import json
import re


## Return all the farms for which the user is is either a farmer
## or a user, and has at least one field assigned

def farms_filter(user):
    farms = Farm.objects.filter( Q(farmer=user) |
                                 Q(users=user) ).distinct()

    # Filter out the farms with no fields
    ret = []
    for field in Field.objects.all():
        if field.farm in farms:
            ret.append(field.farm)
    return list(set(ret))

        

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


    def get_farm_fields(self):
        """
        Creates a dictionary with a farm as the key,
        the list of fields as the value.
        """
        farm_fields = {}
        for farm in farms_filter(self.request.user):
            fields = []
            for field in farm.get_fields():
                fields.append(field)
            farm_fields[farm] = fields

        return farm_fields



    def get_notifications_list(self):
        """
        Get all the notifications for this user and any crop season not yet
        ended. Will include crop seasons not yet started.
        """


        ### TODO Really just need the farm filter here. Used this inearlier
        ### version because the dictionary was usedinother place. No longer the
        ### case.
        farm_field_list = self.get_farm_fields()

        # Might be easier way, this will work for now.
        # But the commented filter does not work.
        notifications_rule_list = [] #NotificationsRule.objects.filter(Q(field_list__in=farm_field_list)).all

        for notify in NotificationsRule.objects.all():

            if not notify.field_list.all(): 
                print "There is a notification record saved without fields. should not happen. Will just ignore for now."
                continue
            aField = notify.field_list.all()[0]
            if farm_field_list.get(aField.farm) is not None:
                notifications_rule_list.append(notify)
        return notifications_rule_list


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
        context['notifications_types']  = NotificationsRule.NOTIFICATION_TYPE_VALUES
        context['alert_levels']         = get_available_levels
        context['available_times']      = get_available_times
        context['available_timezones']  = get_available_timezones
        return context



# May want to move somewhere else. May need again.

class ValidID:

    """
    Create a valid string that can be used as a valid 'id' element
    in HTML by replacing all non-word characters with underscores.
    Will not guarantee uniqueness since "a b" and "a-b" will both
    generate "a_b", but this is the callers responsibility.
    """
    def __init__(self, value):

        self.value = value
        self.id = re.sub('\W', "_", value)



#########################################################################
### Ajax Code
### Below is the ajax code to generate a list of fields and users 
### based on the farm.
#########################################################################


# @method_decorator(login_required)
def get_fields_list(request, **kwargs):

    """
    Get all the fields from the given farm which are part of a currently
    active crop season.
    """

    if not request.is_ajax():       
        raise PermissionDenied()

    farm_pk = request.GET['farm_pk']
    results = []
    farm = Farm.objects.get(pk = farm_pk)
    for f in farm.get_fields():
        print "Adding ", f, " to result"
        f_json = {}
        f_json['id'] = f.pk
        f_json['label'] = f.name
        f_json['value'] = f.name
        results.append(f_json)

    data = json.dumps(results)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def get_users_list(request,  **kwargs):
    """
    Returns all the users, plus the farmer. Remove the duplicate
    if the user is also the owner.
    """

    if not request.is_ajax():       
        raise PermissionDenied()

    farm_pk = request.GET['farm_pk']
    results = []

    for u in Farm.objects.get(pk = farm_pk).get_farmer_and_user_objects():
        print "Adding ", u, " to result"
        u_json = {}
        u_json['id'] = u.pk
        u_json['label'] = str(u)
        u_json['value'] = str(u)
        results.append(u_json)

    data = json.dumps(results)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)
