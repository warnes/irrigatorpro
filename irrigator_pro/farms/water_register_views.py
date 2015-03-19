from django.shortcuts import get_object_or_404, redirect, render, render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.db.models import Q
from django.utils import timezone

import json
import os


from farms.models import CropSeason, Field, WaterRegister
from farms.generate_water_register import generate_water_register

import datetime
from datetime import date

class WaterRegisterListView(ListView):
    template_name = "farms/water_register_list.html"
    model = WaterRegister
    fields = [ 'crop_season',
               'field',
               'date',
               'crop_stage',
               'daily_water_use',
               'rain',
               'irrigation',
               'average_water_content',
               'computed_from_probes',
               'irrigate_flag',
               'check_sensors_flag',
               'dry_down_flag',
               'message'
             ]



    ## User can specify a date for the report on the page.

    # def get(self, request, *args, **kwargs):
    #     print "into get: ", request.GET.get('date')
    #     the_date = request.GET.get('date')
    #     if the_date is not None:
    #         print 'We have a date: ', the_date
    #         self.report_date = datetime.strptime(the_date, "%Y-%m-%d").date()
    #     else:
    #         self.report_date = self.crop_season.season_end_date

    #     return render(request, self.template_name, self.get_context_data())




    def update_water_register(self, crop_season, field, today):
        generate_water_register(crop_season, field, self.request.user, None, today)


    def get_queryset(self):
        queryset = WaterRegister.objects.filter(crop_season=self.crop_season,
                                                field=self.field)

        # self.report_date = datetime.date.today()
        # if self.year is not None:
        #     self.report_date = datetime.date(self.year, self.month, self.day)

        self.update_water_register(self.crop_season, self.field, self.report_date)

        if not queryset.count():
            print "No Water_Register records"
            self.nb_records = 0
            return queryset

        field = self.field
        farm = field.farm

        farmer = farm.farmer
        users  = farm.users.all()
        user_list = [ x for x in  users ]
        user_list.append(farmer)

        if not self.request.user in user_list:
            redirect( reverse('home') )

        # Add report_date to request so it can be used for the plots
        self.request.session['report_date'] = self.report_date.isoformat()
        self.nb_records = len(queryset.distinct())
        print 'nb_records: ', self.nb_records
        return queryset.distinct()


    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.crop_season =  CropSeason.objects.get(pk=int(kwargs.get('season', None)))
        self.field       = Field.objects.get(pk=int(kwargs.get('field', None)))

        self.report_date = min(self.crop_season.season_end_date, date.today())
        print 'report date: ', self.report_date
        
        return super(WaterRegisterListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):


        context = super(WaterRegisterListView, self).get_context_data(**kwargs)
        context['crop_season'] = self.crop_season
        context['field']       = self.field
        context['report_date'] = self.report_date
        context['cwd'] = os.getcwd # Needed?
        context['nb_records'] = self.nb_records # Needed?

        return context

