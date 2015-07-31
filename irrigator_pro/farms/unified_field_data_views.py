from extra_views import ModelFormSetView
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
#from farms.generate_water_register import generate_water_register
from farms.unified_field_data import generate_objects
from farms.utils import to_faren, to_inches

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
        'source',
        'datetime',
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
        'source': HiddenInput(),
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

        # Add report_date to request so it can be used for the plots
        self.request.session['report_date'] = self.report_date.isoformat()

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
            obj.delete()

        for form in formset.forms:
            if form.cleaned_data['DELETE']:
                if DEBUG: print 'Should have been deleted'

            else:
                if "id_"+form.prefix+"-id"  in changed_form_ids:

                    print "pk for object: ", form.cleaned_data['id'].pk
                    print "comment for object: ", form.cleaned_data['comment']
                    print "source for object: ", form.cleaned_data['source']

                    ### If this is a UGA WH just save the ignore, comment directly to DB, don't
                    ### save form since it will mess the other values.

                    if form.cleaned_data['id'].source == "UGA":
                        obj = WaterHistory.objects.get(pk = form.cleaned_data['id'].pk)
                        obj.ignore = form.cleaned_data['ignore']
                        obj.comment = form.cleaned_data['comment']
                        obj.save()

                    else:
                        ### Convert values if necessary
                        obj = form.save(commit=False)
                        if self.request.POST['temp_units']=='C':
                            obj.min_temp_24_hours = to_faren(obj.min_temp_24_hours)
                            obj.max_temp_24_hours = to_faren(obj.max_temp_24_hours)
                        
                        if self.request.POST['depth_units']=='cm':
                            obj.rain = to_inches(obj.rain)
                            obj.irrigation = to_inches(obj.irrigation)

                        ### Update the datetime field. The date itself does not change,
                        ### but the time may have.
                        ### Will only have a value for User WH object.
                        new_time = self.request.POST.get("manual-entry-time-" + form.prefix[5:])
                        if new_time:
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
                obj.min_temp_24_hours = to_faren(obj.min_temp_24_hours)
                obj.max_temp_24_hours = to_faren(obj.max_temp_24_hours)

            if self.request.POST['depth_units']=='cm':
                obj.rain = to_inches(obj.rain)
                obj.irrigation = to_inches(obj.irrigation)

            new_time = self.request.POST["form-" + form.prefix[5:] + "-time"]

            hr_min = re.search("(\d+):(\d+)", new_time)
            obj.datetime = obj.datetime.replace(hour=int(hr_min.group(1)), minute=int(hr_min.group(2)))
            obj.save()
                

            obj.save()



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

