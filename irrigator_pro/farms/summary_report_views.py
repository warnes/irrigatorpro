from django.shortcuts import get_object_or_404, redirect, render, render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.db.models import DateField
from django.utils import timezone

from farms.models import CropSeason, Field, WaterRegister, Farm, CropSeasonEvent
from farms.generate_water_register import generate_water_register


class SummaryReportListView(ListView):
    template_name = "farms/summary_report.html"
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

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.farm        = Farm.objects.get(pk=int(kwargs.get('farm', None)))
        self.crop_season = CropSeason.objects.get(pk=int(kwargs.get('crop_season', None)))

        return super(SummaryReportListView, self).dispatch(*args, **kwargs)



    def get_queryset(self):
        queryset = self.get_object_list()
        return queryset




    #####################################################
    ## Method to gather data and create the query set. ##
    #####################################################

    def get_object_list(self):
        ret_list = []
        for field in self.crop_season.field_list.all():
            if (field.farm == self.farm):
                srf = SummaryReportFields()
                srf.field = field
                ret_list.append(srf)

                # Get the water registry for the crop season / field

                wr = WaterRegister.objects.filter(crop_season = self.crop_season, field = field).latest('date')
                if (wr is not None):
                    srf.growth_stage    = wr.crop_stage
                    srf.dwu             = wr.daily_water_use
                    srf.awc             = wr.average_water_content
                    srf.cumulative_rain = wr.rain
                    srf.cumulative_irrigation_vol = wr.irrigation

                # Get the last event
                cse = CropSeasonEvent.objects.latest('date')
                if (cse is not None):
                    srf.time_last_data_entry = cse.date
                    srf.last_data_entry_type = cse.get_event_description

        return ret_list


    def get_context_data(self, **kwargs):
        context = super(SummaryReportListView, self).get_context_data(**kwargs)
        context['crop_season'] = self.crop_season
        return context



class SummaryReportFields:

    # Provide default values for all the fields
    field                       = 'Unknown field'
    growth_stage                = 'Undetermined stage'
    dwu                         = 0.0
    awc                         = 0.0
    next_irrigation_date        = False
    link_to_water_reg           = ''
    last_data_entry_type        = ''
    time_last_data_entry = DateField(default=timezone.now())
    cumulative_rain             = 0.0
    cumulative_irrigation_vol   = 0.0

    
    
    
    
