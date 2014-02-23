from extra_views import InlineFormSet, CreateWithInlinesView, ModelFormSetView, UpdateWithInlinesView
from django.forms import MultipleChoiceField, Textarea, TextInput
from django.db.models import Q
from django.core.urlresolvers import reverse

from farms.models import Probe, WaterHistory

from farm_views import *
from planting_views import *


def fields_filter(user):
        return Field.objects.filter( Q(farm__farmer=user) |
                                     Q(farm__users=user) ).distinct()


class ProbesView(ModelFormSetView):
    model = Probe

    template_name = 'farms/probe_list.html'

    fields = [ 'name', 'description', 'field_list', 'farm_code', 'probe_code', 'comment'] 
    widgets = {
        'comment':     Textarea(attrs={'rows':2, 'cols':20}),
        'description': Textarea(attrs={'rows':2, 'cols':20}),
    }

    can_delete=True

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProbesView, self).dispatch(*args, **kwargs)
    
    def get_queryset(self):
        user = self.request.user
        queryset = super(ProbesView, self).get_queryset()

        queryset = queryset.filter( Q(field_list__farm__farmer=user) | 
                                    Q(field_list__farm__users=user) 
                                  )
        
        return queryset.distinct()

    def construct_formset(self, *args, **kwargs):
        formset = super(ProbesView, self).construct_formset(*args, **kwargs)
        print formset
        for form in formset:
            form.fields["field_list"].queryset = fields_filter(self.request.user)
        return formset

    def get_factory_kwargs(self):
        kwargs = super(ProbesView, self).get_factory_kwargs()
        if hasattr(self, 'widgets'):
            kwargs[ 'widgets' ] = self.widgets
        return kwargs



class WaterHistoryView(ModelFormSetView):
    model = WaterHistory

    template_name = 'farms/water_history_list.html'

    fields = [ 'date', 'field_list',  'rain', 'irrigation', 'comment' ]
    widgets = {
        'comment':     Textarea(attrs={'rows':2, 'cols':20}),
        'description': Textarea(attrs={'rows':2, 'cols':20}),
        'date':        TextInput(attrs={'width':10, 'class':'hasDatePicker'}),
    }

    can_delete=True

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(WaterHistoryView, self).dispatch(*args, **kwargs)
    
    def get_queryset(self):
        user = self.request.user
        queryset = super(WaterHistoryView, self).get_queryset()

        queryset = queryset.filter( Q(field_list__farm__farmer=user) | 
                                    Q(field_list__farm__users=user) 
                                  )
        
        return queryset.distinct()

    def construct_formset(self, *args, **kwargs):
        formset = super(WaterHistoryView, self).construct_formset(*args, **kwargs)
        for form in formset:
            form.fields["field_list"].queryset = fields_filter(self.request.user) 
            print form.fields["comment"]
        return formset

    def get_factory_kwargs(self):
        kwargs = super(WaterHistoryView, self).get_factory_kwargs()
        if hasattr(self, 'widgets'):
            kwargs[ 'widgets' ] = self.widgets
        return kwargs

