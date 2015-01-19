from django.shortcuts import get_object_or_404, redirect, render, render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.db.models import DateField
from django.utils import timezone
from django.db.models import Q

from farms.models import Farm, CropSeason, Field, WaterRegister, WaterHistory, Farm, CropSeasonEvent, Probe, ProbeReading

from datetime import date, datetime

## Defined in farms_views.py as well. Factorize?

def farms_filter(user):
    return Farm.objects.filter( Q(farmer=user) |
                                Q(users=user) ).distinct()



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

    #####################################################
    ## Method to gather data and create the query set. ##
    ## Get information for all the farms this user has ##
    ## access to, and only return info for active      ##
    ## fields on these farms.                          ##
    #####################################################

    def get_object_list(self):
        ret_list = []
        #        image = plot_daily_use(self.request)


        print "Year: ", self.year

        # For testing allow URL to end with .../summary_report/2013/07/31
        self.today_date = date.today()
        if self.year is not None:
            self.today_date = date(self.year, self.month, self.day)


 
        farm_list = farms_filter(self.request.user)

        # TODO Change the date for either today, or a date given in the url for debugging purpose.
        crop_season_list = CropSeason.objects.filter(season_start_date__lt = self.today_date,
                                                     season_end_date__gte = self.today_date).all()

        # Create a dictionary with ('field', 'crop_season')
        all_fields = {}
        for x in crop_season_list:
            for field in x.field_list.all():
                all_fields[field] = x
    

        ## TODO Much too long, hard to follow. Break down into subroutines.


        for farm in farm_list:

            field_list = Field.objects.filter(farm = farm)
            for field in field_list:

                # Get all the crop_season objects that:
                #    - field_list contains the field

                if field not in all_fields: continue
                crop_season = all_fields[field]
                
                # Will add an entry for this field and farm

                srf = SummaryReportFields()
                srf.field = field
                srf.farm = farm
                srf.crop = crop_season.crop
                ret_list.append(srf)

                # Get the water registry for the crop season / field

                wr = WaterRegister.objects.filter(crop_season = all_fields[field], field = field).latest('date')
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

                    whList = WaterHistory.objects.filter(crop_season = crop_season)
                    # Just keep the ones with one of the fields equal to current fiels.
                    
                    if (whList is not None):
                        latestWH = whList.filter(field_list = field) #.latest('date')
                        latest_water_record = whList.latest('date')

                    # Now get the latest measurement record from the probes.
                    # First all the probes for a given pair (field, crop season)

                    probe_list = Probe.objects.filter(field_list = field, crop_season = crop_season)
                    if (len(probe_list) > 0):
                        radio_id = probe_list[0].radio_id
                        probe_readings = ProbeReading.objects.filter(radio_id = radio_id)
                        # Same radio id can be used across seasons. Filter based on (Start, end) of 
                        # crop season
                        probe_readings = probe_readings.filter(reading_datetime__gte = crop_season.season_start_date,
                                                               reading_datetime__lte = crop_season.season_end_date)
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
                    srf.water_registry_url = self.request.get_host() +'/water_register/' + str(crop_season.pk) + '/' + str(field.pk)

                    # Add the water register object to get next irrigation date, or status.
                    # Only add if planting season is not over.
                    if (crop_season.season_end_date >= date.today()):
                        srf.water_registry_object = wr
                
        return ret_list


    def get_context_data(self, **kwargs):
        context = super(SummaryReportListView, self).get_context_data(**kwargs)
        context['today_date'] = self.today_date
        return context


    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):

        # There are either parameters for year, month, day, or none.
        year_param = kwargs.get('year', None)
        if year_param is not None:
            self.year = int(year_param)
            self.month= int(kwargs.get('month', None))
            self.day = int(kwargs.get('day', None))
        return super(SummaryReportListView, self).dispatch(*args, **kwargs)


    def get_queryset(self):
        queryset = self.get_object_list()
        return queryset



class SummaryReportFields:

    # Provide default values for all the fields
    farm                        = 'Unknown farm'
    field                       = 'Unknown field'
    crop                        = 'Unknown crop'
    growth_stage                = 'Undetermined stage'
    dwu                         = 0.0
    awc                         = 0.0
    link_to_water_reg           = ''
    last_data_entry_type        = ''
    time_last_data_entry        = DateField(default=timezone.now())
    cumulative_rain             = 0.0
    cumulative_irrigation_vol   = 0.0
    water_registry_url          = ''
    water_registry_object       = None
    
    
    
    
