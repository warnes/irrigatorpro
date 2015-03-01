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

from django.views.generic import TemplateView

from farms.models import Farm, CropSeason, Field, WaterRegister, WaterHistory, Farm, CropSeasonEvent, Probe, ProbeReading
from farms.generate_water_register import generate_water_register

from datetime import date, datetime

## Defined in farms_views.py as well. Factorize?

def farms_filter(user):
    return Farm.objects.filter( Q(farmer=user) |
                                Q(users=user) ).distinct()


# Could probably use lamdba...
def cumulative_water(wr_list):
    total_rain = 0
    total_irr = 0
    for wr in wr_list:
        total_rain += wr.rain
        total_irr += wr.irrigation

    return (total_rain, total_irr)




class SummaryReportListView(TemplateView):
    template_name = "farms/summary_report.html"



    def get(self, request, *args, **kwargs):
        print "into get: ", request.GET.get('date')
        the_date = request.GET.get('date')
        if the_date is not None:
            print 'We have a date: ', the_date
            self.report_date = datetime.strptime(the_date, "%Y-%m-%d").date()
        else:
            self.report_date = date.today()

        return render(request, self.template_name, self.get_context_data())



    #####################################################
    ## Method to gather data and create the query set. ##
    ## Get information for all the farms this user has ##
    ## access to, and only return info for active      ##
    ## fields on these farms.                          ##
    #####################################################

    def get_object_list(self):
        ret_list = []
            
        farm_list = farms_filter(self.request.user)

        crop_season_list = CropSeason.objects.filter(season_start_date__lt = self.report_date,
                                                     season_end_date__gte = self.report_date).all()

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
                generate_water_register(crop_season,
                                        field,
                                        self.request.user,
                                        None,
                                        self.report_date)

                
                # Will add an entry for this field and farm

                srf = SummaryReportFields()
                srf.field = field
                srf.farm = farm
                srf.crop = crop_season.crop
                ret_list.append(srf)

                # Get the water registry for the crop season / field

                wr_list = WaterRegister.objects.filter(crop_season = crop_season, 
                                                       field = field).order_by('-date').filter(Q(date__lte =  self.report_date))
        
                
                
                if len(wr_list) == 0: continue
                wr = wr_list[0]
                if (wr is not None):
                    srf.growth_stage    = wr.crop_stage
                    srf.message         = wr.message
                    (srf.cumulative_rain, srf.cumulative_irrigation_vol) = cumulative_water(wr_list)
                    srf.days_to_irrigation = wr.days_to_irrigation

                    # Get the last event for the field. It will be either rain, irrigation,
                    # manual reading or automated reading.

                    # First get the latest water event from water history
                    # The water history contains a field list (although right now it
                    # may be limited to one field.) Still, assume there could be more
                    # than one.

                    whList = WaterHistory.objects.filter(crop_season = crop_season)
                    # Just keep the ones with one of the fields equal to current fiels.
                    
                    latest_water_record = None
                    if len(whList) > 0:
                        latestWH = whList.filter(field_list = field) #.latest('date')
                        latest_water_record = whList.latest('date')

                    # Now get the latest measurement record from the probes.
                    # First all the probes for a given pair (field, crop season)

                    probe_list = Probe.objects.filter(field_list = field, crop_season = crop_season)
                    latest_probe_reading = None
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
                    latest_is_wr = None
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
                            # Ensure we have a datetime object for consistency in data
                            x = latest_water_record.date
                            srf.time_last_data_entry = datetime(x.year, x.month, x.day)
                        else:
                            srf.last_data_entry_type = "Probe reading"
                            srf.time_last_data_entry = latest_probe_reading.reading_datetime
            
                    # Add link to water register
                    srf.water_register_url = self.request.get_host() +'/water_register/' + str(crop_season.pk) + '/' + str(field.pk)

                    # Add the water register object to get next irrigation date, or status.
                    # Only add if planting season is not over.
                    if (crop_season.season_end_date >= self.report_date):
                        srf.water_register_object = wr
                
        return ret_list


    def get_context_data(self, **kwargs):
        context = super(SummaryReportListView, self).get_context_data(**kwargs)
        context['report_date'] = self.report_date
        context['object_list'] = self.get_object_list()
        return context


    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SummaryReportListView, self).dispatch(*args, **kwargs)



class SummaryReportFields:

    # Provide default values for all the fields
    farm                        = 'Unknown farm'
    field                       = 'Unknown field'
    crop                        = 'Unknown crop'
    growth_stage                = 'Undetermined stage'
    link_to_water_reg           = ''
    last_data_entry_type        = 'No Entry'
    time_last_data_entry        = 'No Entry' #DateField(default=timezone.now())
    cumulative_rain             = 0.0
    cumulative_irrigation_vol   = 0.0
    days_to_irrigation          = 0
    water_register_url          = ''
    water_register_object       = None
    message                     = 'something'
