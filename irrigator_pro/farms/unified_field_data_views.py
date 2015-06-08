from extra_views import ModelFormSetView

from django.utils.datastructures import MultiValueDictKeyError

from django.shortcuts import get_object_or_404, redirect, render, render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.db.models import Q
from django.utils import timezone

from django.http import HttpResponseRedirect

import os

from farms.models import CropSeason, Field, WaterRegister, WaterHistory
from farms.generate_water_register import generate_water_register
from farms.unified_field_data import generate_objects
#from farms.forms import WaterHistoryForm


from datetime import date, datetime

class UnifiedFieldDataEmptyView(TemplateView):
    template_name = 'farms/water_register_empty.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UnifiedFieldDataEmptyView, self).dispatch(*args, **kwargs)

######################################################################
### Views class for the unified view of fields data: rain, irrigation,
### temps, etc as well as computer values from the water register.
### 


class UnifiedFieldDataListView(ModelFormSetView):
    template_name = "farms/unified_field_data_list.html"
    model = WaterHistory
    fields = [
        'date',
        'soil_potential_8',
        'soil_potential_16',
        'soil_potential_24',
        'min_temp_24_hours',
        'max_temp_24_hours',
        'ignore',
        'rain',
        'irrigation'
    ]


    #    def update_water_register(self, crop_season, field, today):
    #        generate_water_register(crop_season, field, self.request.user, None, today)


    



    def get(self, request, *args, **kwargs):
        print "Into get"
        (self.wh_formset, self.object_list) = generate_objects(self.crop_season, 
                                                               self.field, 
                                                               self.request.user,
                                                               self.report_date)

        return render(request, self.template_name, self.get_context_data())




    # def post(self, request, *args, **kwargs):

    #     print "Into unified_field_data_view.py"



    #     return HttpResponseRedirect(reverse("unified_water_season_field",
    #                                         kwargs={'season': self.crop_season.pk,
    #                                                 'field': self.field.pk}))



    def formset_valid(self, formset):
        print "Into formset_valid"

    def formset_invalid(self, formset):
        print "Into formset_invalid"
        print formset.errors




    # def get_queryset(self):
    #     self.update_water_register(self.crop_season, self.field, self.report_date)

    #     queryset = WaterRegister.objects.filter(crop_season=self.crop_season,
    #                                             field=self.field)


    #     if not queryset.count():
    #         print "No Water_Register records"
    #         self.nb_records = 0
    #         return queryset

    #     field = self.field
    #     farm = field.farm

    #     farmer = farm.farmer
    #     users  = farm.users.all()
    #     user_list = [ x for x in  users ]
    #     user_list.append(farmer)

    #     if not self.request.user in user_list:
    #         redirect( reverse('home') )

    #     # Add report_date to request so it can be used for the plots
    #     self.request.session['report_date'] = self.report_date.isoformat()
    #     self.nb_records = len(queryset.distinct())
    #     print 'nb_records: ', self.nb_records
    #     return queryset.distinct()


    # def get_object_list(self):
    #     ret_list = generate_objects(self.crop_season, self.field, self.request.user, self.report_date)
    #     return ret_list


    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        print "Into dispatch"
        self.crop_season = CropSeason.objects.get(pk=int(kwargs.get('season', None)))
        self.field       = Field.objects.get(pk=int(kwargs.get('field', None)))
        try:
            dateStr          = kwargs.get('date', None)
            self.report_date = datetime.strptime(dateStr, "%Y-%m-%d").date()
        except: 
            self.report_date = min(self.crop_season.season_end_date, date.today())


        try:
            return super(UnifiedFieldDataListView, self).dispatch(*args, **kwargs)
        except MultiValueDictKeyError as e:
            print "Error returned: ", e

    def get_context_data(self, **kwargs):

        context = super(UnifiedFieldDataListView, self).get_context_data(**kwargs)
        context['object_list']  = self.object_list
        context['wh_formset']   = self.wh_formset
        context['crop_season']  = self.crop_season
        context['field']        = self.field
        context['report_date']  = self.report_date
        context['cwd']          = os.getcwd # Needed?
#        context['nb_records']  = self.nb_records # Needed?

        return context

