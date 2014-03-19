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
             ]


    def update_water_register(self, crop_season, field):
        ## calculate new data ##
        table_header, table_rows = generate_water_register(crop_season, field)

        ## insert new data into database ##
        if table_rows:
            for row in table_rows:

                print row
                
                try: 
                    wr = WaterRegister.objects.get(crop_season=crop_season, 
                                                   field=field, 
                                                   date=row[2])
                except:
                    wr = WaterRegister()

                ( wr.crop_season, #0
                  wr.field,       #1
                  wr.date,        #2
                  wr.crop_stage,
                  wr.daily_water_use,
                  wr.rain,
                  wr.irrigation,
                  wr.average_water_content,
                  wr.computed_from_probes,
                  wr.irrigate_flag,
                  wr.check_sensors_flag, ) = row
                
                wr.cuser = self.request.user
                wr.muser = self.request.user
                
                wr.save()


    ## This method needs optimization for performance ##
    ## 1: Only recompute *if* underlying water_history or probe_reading data has changed,
    ## 2: Use a date range filter with default range that spans +2/-2 weeks
    def get_queryset(self):
        queryset = WaterRegister.objects.filter(crop_season=self.crop_season,
                                                field=self.field)

        if True:
            ## remove old data ##
            queryset.all().delete()

            ## generate new data ##
            self.update_water_register(self.crop_season, self.field)

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

        return queryset.distinct()

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.crop_season = CropSeason.objects.get(pk=int(kwargs.get('season', None)))
        self.field       = Field.objects.get(pk=int(kwargs.get('field', None)))

        return super(WaterRegisterListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(WaterRegisterListView, self).get_context_data(**kwargs)
        context['crop_season'] = self.crop_season
        context['field']       = self.field
        return context

