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
from django.forms.widgets import HiddenInput as HiddenInput

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
        'crop_season',
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
    widgets  = {
        'crop_season': HiddenInput(),
        'date': HiddenInput(),
        'field_list': HiddenInput()
    }
    extra = 0

    def get(self, request, *args, **kwargs):

        self.wh_formset = self.construct_formset() #super(UnifiedFieldDataListView, self).construct_formset()
        self.object_list = generate_objects(self.wh_formset,
                                            self.crop_season, 
                                            self.field, 
                                            self.request.user,
                                            self.report_date)

        return render(request, self.template_name, self.get_context_data())



    def get_factory_kwargs(self):

        kwargs = super(UnifiedFieldDataListView, self).get_factory_kwargs()
        if hasattr(self, 'widgets'):
            kwargs[ 'widgets' ] = self.widgets
        return kwargs

    def get_queryset(self):
        query = super(UnifiedFieldDataListView, self).get_queryset().filter(crop_season=self.crop_season,
                                                                            field_list=self.field).all().order_by("date")
        return query



    ### Does nothing now. Remove if stays this way.
    def construct_formset(self):
        formset = super(UnifiedFieldDataListView, self).construct_formset()
        return formset


    def formset_valid(self, formset):

        formset.save()
        ### The field list is not part of the form. Add to new objects
        for wh in formset.new_objects:
            wh.field_list.add(self.field)
            wh.save()
        ### TODO Add processing for deleted objects.

        return HttpResponseRedirect(reverse("unified_water_season_field",
                                            kwargs={'season': self.crop_season.pk,
                                                    'field': self.field.pk}))



    def formset_invalid(self, formset):

        self.wh_formset = formset
        self.object_list = generate_objects(formset,
                                            self.crop_season, 
                                            self.field, 
                                            self.request.user,
                                            self.report_date)
        
        return self.render_to_response(self.get_context_data())



    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):

        self.crop_season = CropSeason.objects.get(pk=int(kwargs.get('season', None)))
        self.field       = Field.objects.get(pk=int(kwargs.get('field', None)))
        try:
            dateStr          = kwargs.get('date', None)
            self.report_date = datetime.strptime(dateStr, "%Y-%m-%d").date()
        except: 
            self.report_date = min(self.crop_season.season_end_date, date.today())


        return super(UnifiedFieldDataListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super(UnifiedFieldDataListView, self).get_context_data(**kwargs)
        context['object_list']  = self.object_list
        context['wh_formset']   = self.wh_formset
        context['crop_season']  = self.crop_season
        context['field']        = self.field
        context['report_date']  = self.report_date

        return context

