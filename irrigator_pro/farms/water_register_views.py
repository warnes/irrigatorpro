from django.shortcuts import get_object_or_404, redirect, render, render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.db.models import Q
from django.utils import timezone

from farms.models import CropSeason, Field, WaterRegister
from farms.generate_water_register import generate_water_register

import datetime

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

    def update_water_register(self, crop_season, field, today):
        generate_water_register(crop_season, field, self.request.user, None, today)



    ## This method needs optimization for performance ##
    ## 1: Only recompute *if* underlying water_history or probe_reading data has changed,
    ## 2: Use a date range filter with default range that spans +2/-2 weeks
    def get_queryset(self):
        queryset = WaterRegister.objects.filter(crop_season=self.crop_season,
                                                field=self.field)

        ##if True:
            ## remove old data ##
        ##    queryset.all().delete()

        ## generate new data ##

        # For testing allow URL to end with .../summary_report/2013/07/31
        self.today_date = datetime.date.today()
        if self.year is not None:
            self.today_date = datetime.date(self.year, self.month, self.day)

        self.update_water_register(self.crop_season, self.field, self.today_date)

        if not queryset.count():
            return queryset

        field = queryset[0].field
        farm = field.farm

        farmer = farm.farmer
        users  = farm.users.all()
        user_list = [ x for x in  users ]
        user_list.append(farmer)

        if not self.request.user in user_list:
            redirect( reverse('home') )

        # Add today_date to request so it can be used for the plots
        self.request.session['today_date'] = self.today_date.isoformat()
        return queryset.distinct()

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.crop_season =  CropSeason.objects.get(pk=int(kwargs.get('season', None)))
        self.field       = Field.objects.get(pk=int(kwargs.get('field', None)))
        self.year = None
        year_param = kwargs.get('year', None)
        if year_param is not None:
            self.year = int(year_param)
            self.month= int(kwargs.get('month', None))
            self.day = int(kwargs.get('day', None))
        return super(WaterRegisterListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(WaterRegisterListView, self).get_context_data(**kwargs)
        context['crop_season'] = self.crop_season
        context['field']       = self.field
        context['today_date'] = self.today_date

        return context

