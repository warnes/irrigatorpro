from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.db.models import Q
from django.core.context_processors import csrf

from django.contrib.auth.models import User


from django.http import HttpResponseRedirect

from datetime import date, datetime

from notifications.models import NotificationsRule, Field

from farms.models import CropSeason, Farm, Field

def farms_filter(user):
    return Farm.objects.filter( Q(farmer=user) |
                                Q(users=user) ).distinct()

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
        print "Into post"

        pk = request.POST["pk"]
        print "pk of row to add or edit: ", pk
        if (pk == "-1"):
            print "New Rule"
            notifications = NotificationsRule()
        else:
            print "Existing rule"
            notifications = NotificationsRule.objects.get(pk = pk)
            notifications.recipients.clear()
            notifications.field_list.clear()

        

        notifications.save()
        
        for x in request.POST.getlist("select-fields"):
            print "Adding field: ", x
            notifications.field_list.add(Field.objects.get(pk=x))

        print request.POST.get('communication-type')
        notifications.notification_type = request.POST.get('communication-type')

        print request.POST.get('alert-level')
        notifications.level = request.POST.get('alert-level')

        for x in request.POST.getlist("select-users"):
            print "Adding user: ", x
            notifications.recipients.add(User.objects.get(pk=x))

        

        notifications.save();
        return HttpResponseRedirect('')  # back to the same page


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
                print "Adding ", field, " to ", farm
                fields.append(field)
            farm_fields[farm] = fields

        print "returning ", farm_fields
        return farm_fields



    def get_farm_users(self):
        farm_users = {}
        for farm in farms_filter(self.request.user):
            users = []
            for user in farm.get_farmer_and_user_objects():
                print "Adding ", user, " to ", farm
                users.append(user)
            farm_users[farm] = users

        print "returning ", farm_users
        return farm_users




    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        print "Into dispatch"
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
        context['alert_levels']         = NotificationsRule.LEVEL_CHOICES
        return context
