from extra_views import ModelFormSetView
from django.forms import Textarea, TextInput
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from farms.models import Field, Probe, ProbeReading, WaterHistory
from fields_filter import *

class Farms_FormsetView(ModelFormSetView):
    # model = WaterHistory
    # template_name = 'farms/water_history_list.html'
    # fields = [ 'date', 'field_list',  'rain', 'irrigation', 'comment' ]
    # widgets = {
    #    'comment':     Textarea(attrs={'rows':2, 'cols':20}),
    #    'description': Textarea(attrs={'rows':2, 'cols':20}),
    #    'date':        TextInput(attrs={'width':10, 'class':'hasDatePicker'}),
    #    }

    can_delete=True

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
            return super(Farms_FormsetView, self).dispatch(*args, **kwargs)
            
    def get_queryset(self):
        user = self.request.user
        queryset = super(Farms_FormsetView, self).get_queryset()

        queryset = queryset.filter( Q(field_list__farm__farmer=user) | 
                                    Q(field_list__farm__users=user) 
        )
        
        return queryset.distinct()

    def fields_filter(self, user):
        return Field.objects.filter( Q(farm__farmer=user) |
                                     Q(farm__users=user) ).distinct()

    def construct_formset(self, *args, **kwargs):
        formset = super(Farms_FormsetView, self).construct_formset(*args, **kwargs)
        for form in formset:
            form.fields["field_list"].queryset = self.fields_filter(self.request.user) 
            print form.fields["comment"]
        return formset

    def get_factory_kwargs(self):
        kwargs = super(Farms_FormsetView, self).get_factory_kwargs()
        if hasattr(self, 'widgets'):
            kwargs[ 'widgets' ] = self.widgets
        return kwargs


class ProbeFormsetView(Farms_FormsetView):
    model = Probe
    template_name = 'farms/probe_list.html'
    fields = [ 'name', 'description', 'field_list', 'farm_code', 'probe_code', 'comment'] 
    widgets = {
        'comment':     Textarea(attrs={'rows':2, 'cols':20}),
        'description': Textarea(attrs={'rows':2, 'cols':20}),
    }

class WaterHistoryFormsetView(Farms_FormsetView):
    model = WaterHistory
    template_name = 'farms/water_history_list.html'
    fields = [ 'date', 'field_list',  'rain', 'irrigation', 'comment' ]
    widgets = {
        'comment':     Textarea(attrs={'rows':2, 'cols':20}),
        'description': Textarea(attrs={'rows':2, 'cols':20}),
        'date':        TextInput(attrs={'width':10, 'class':'hasDatePicker'}),
    }
