from django.shortcuts import get_object_or_404, redirect, render, render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.db.models import DateField
from django.utils import timezone

from farms.models import CropSeason, Field, WaterRegister, WaterHistory, Farm, CropSeasonEvent, Probe, ProbeReading
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

                # Get the last event for the field. It will be either rain, irrigation,
                # manual reading or automated reading.

                # First get the latest water event from water history
                # The water history contains a field list (although right now it
                # may be limited to one field.) Still, assume there could be more
                # than one.

                whList = WaterHistory.objects.filter(crop_season = self.crop_season)
                # Just keep the ones with one of the fields equal to current fiels.

                if (whList is not None):
                    latestWH = whList.filter(field_list = field) #.latest('date')
                    latest_water_record = whList.latest('date')

                # Now get the latest measurement record from the probes.
                # First all the probes for a given pair (field, crop season)

                probe_list = Probe.objects.filter(field_list = field, crop_season = self.crop_season)
                if (len(probe_list) > 0):
                    radio_id = probe_list[0].radio_id
                    probe_readings = ProbeReading.objects.filter(radio_id = radio_id)
                    # Same radio id can be used across seasons. Filter based on (Start, end) of 
                    # crop season
                    print 'Number of readings: ', len(probe_readings)
                    probe_readings = probe_readings.filter(reading_datetime__gte = self.crop_season.season_start_date,
                                                           reading_datetime__lte = self.crop_season.season_end_date)
                    if (probe_readings is not None):
                        latest_probe_reading = probe_readings.latest('reading_datetime')
                
                        

                # Compare both records, keep most recent.
                # Probably easier way in python to do this. Can worry later.
                if (latest_water_record is None and latest_probe_reading is None): pass
                elif  (latest_water_record is not None and latest_probe_reading is not None):
                    latest_is_wr = True if (latest_water_record.date > latest_probe_reading.reading_datetime.date()) else False
                else:
                    if (latest_water_record is not None):
                        latest_is_wr = True
                    else:
                        latest_is_wr = False
                if (latest_is_wr is not None):
                    if (latest_is_wr):
                        srf.last_data_entry_type = "Rain or irrigation"
                        srf.time_last_data_entry = latest_water_record.date
                    else:
                        srf.last_data_entry_type = "Probe reading"
                        srf.time_last_data_entry = latest_probe_reading.reading_datetime

            
                # Add link to water register
                srf.water_registry_url = self.request.get_host() +'/water_register/' + str(self.crop_season.pk) + '/' + str(field.pk)
                print 'url: ', srf.water_registry_url
                
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
    water_registry_url          = ''

    
    
    
    
