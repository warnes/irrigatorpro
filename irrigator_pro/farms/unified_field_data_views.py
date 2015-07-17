from extra_views import ModelFormSetView
from pprint import pprint
import re
from django.utils.datastructures import MultiValueDictKeyError

from irrigator_pro.settings import DEBUG

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
from django import forms
from django.forms.widgets import HiddenInput as HiddenInput
from django.forms.widgets import TextInput as TextInput
from django.forms.widgets import TimeInput as TimeInput

import os
import types

from farms.models import CropSeason, Field, WaterRegister, WaterHistory, ProbeReading
from farms.generate_water_register import generate_water_register
from farms.unified_field_data import generate_objects
from farms.utils import get_probe_readings, to_faren, to_inches

from datetime import date, datetime

######################################################################
### Views class for the unified view of fields data: rain, irrigation,
### temps, etc as well as computed values from the water register.
### 


class UnifiedFieldDataListView(ModelFormSetView):
    template_name = "farms/unified_field_data_list.html"
    model = WaterHistory
    fields = [
        'crop_season',
        'datetime',
        #'date',
        #'time',
        'soil_potential_8',
        'soil_potential_16',
        'soil_potential_24',
        'min_temp_24_hours',
        'max_temp_24_hours',
        'ignore',
        'rain',
        'irrigation',
        'comment'
    ]
    widgets  = {
        'crop_season': HiddenInput(),
        'date': HiddenInput(),
       'datetime': HiddenInput(),
    }
    extra = 0
    can_delete=True

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
                                                                            field=self.field).all().order_by("datetime")
        return query



    ### Does nothing now. Remove if stays this way.
    def construct_formset(self):
        formset = super(UnifiedFieldDataListView, self).construct_formset()
        return formset



    ##########################################################################
    ###
    ### Save the formset.
    ###
    ### Because user can convert the temperature and depth values in the form
    ### could look like they changed even if they have not.  To avoid saving
    ### objects that have not changed, causing unnecessary recomputation to
    ### the water register, there is a hidden field that is added when a user
    ### clicks in at least one field from a form. This includes the time,
    ### which is not really part of the form.

    def formset_valid(self, formset):

        if DEBUG: print 'Into formset_valid'

        changed_form_ids = self.request.POST.getlist('changed_forms[]')
        formset.save(commit=False)

        ### Any form not in changed_form_ids does not need saving.
        ### For all the other convert if necessary.


        for obj in formset.deleted_objects:
            if DEBUG: print "Will delete: ", obj, " of class ", obj.__class__
            if isinstance(obj, WaterHistory):
                WaterHistory.delete(obj)

        for form in formset.forms:
            if form.cleaned_data['DELETE']:
                if DEBUG: print 'Should have been deleted'

            else:
                if DEBUG: print 'Will not delete, may save'

                if "id_"+form.prefix+"-id"  in changed_form_ids:
                    if DEBUG: print "Will save form with id: ", form.prefix
                    ### Convert values if necessary
                    obj = form.save(commit=False)
                    if self.request.POST['temp_units']=='C':
                        if DEBUG: print "Converting temps from C to F"
                        obj.min_temp_24_hours = to_faren(obj.min_temp_24_hours)
                        obj.max_temp_24_hours = to_faren(obj.max_temp_24_hours)
                        
                    if self.request.POST['depth_units']=='cm':
                        if DEBUG: print "Converting temps from cm to in"
                        obj.rain = to_inches(obj.rain)
                        obj.irrigation = to_inches(obj.irrigation)

                    ### Update the datetime field. The date itself does not change,
                    ### but the time may have.
                    new_time = self.request.POST["manual-entry-time-" + form.prefix[5:]]

                    hr_min = re.search("(\d+):(\d+)", new_time)
                    obj.datetime = obj.datetime.replace(hour=int(hr_min.group(1)), minute=int(hr_min.group(2)))
                    obj.save()


        ### The field  is not part of the form. Add to new objects
        ## Need this in order to create new_objects list
        for obj in formset.new_objects:
            obj.field=self.field
            obj.save(force_update=False)
            ### Copied from above. Need to factor out
            if self.request.POST['temp_units']=='C':
                if DEBUG: print "Converting temps from C to F"
                obj.min_temp_24_hours = to_faren(obj.min_temp_24_hours)
                obj.max_temp_24_hours = to_faren(obj.max_temp_24_hours)

            if self.request.POST['depth_units']=='cm':
                if DEBUG: print "Converting temps from cm to in"
                obj.rain = to_inches(obj.rain)
                obj.irrigation = to_inches(obj.irrigation)

            new_time = self.request.POST["form-" + form.prefix[5:] + "-time"]

            hr_min = re.search("(\d+):(\d+)", new_time)
            obj.datetime = obj.datetime.replace(hour=int(hr_min.group(1)), minute=int(hr_min.group(2)))
            obj.save()
                

            obj.save()


        # ignore name for uga probes in form is uga-ID
        # Here we only receive the ids for the probes that are set to ignore,
        # it doesn't mean there's a change and we want to be sure we don't
        # change anything unnecessarily otherwise we trigger computation
        # of water registers

        ignored = [int(k[4:]) for k in self.request.POST.keys() if 'uga' in k]
        all_probe_readings = get_probe_readings(self.crop_season, self.field)

        if len(all_probe_readings) > 0:
            for pr in all_probe_readings:
                if pr.ignore and pr.pk not in ignored:
                    pr.ignore = False
                    pr.save()
                elif not pr.ignore and pr.pk in ignored:
                    pr.ignore = True
                    pr.save()

        return HttpResponseRedirect(reverse("unified_water_season_field",
                                            kwargs={'season': self.crop_season.pk,
                                                    'field': self.field.pk}))



    def formset_invalid(self, formset):
        if DEBUG: print 'Into formset_invalid'
        if DEBUG: print formset.errors

        self.wh_formset = formset
        self.object_list = generate_objects(formset,
                                            self.crop_season, 
                                            self.field, 
                                            self.request.user,
                                            self.report_date)
        
        return self.render_to_response(self.get_context_data())



    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if DEBUG: print 'Into dispatch'
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

