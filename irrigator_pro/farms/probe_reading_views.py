from extra_views import ModelFormSetView
from django.forms import Textarea, TextInput
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.list import ListView

from farms.models import Probe, ProbeReading

class ProbeReadingFormsetView(ModelFormSetView):
    model = ProbeReading
    template_name = 'farms/formset.html'
    fields = [ 
        'farm_code', 'probe_code', 
        'reading_datetime',
        'soil_potential_8', 'soil_potential_16', 'soil_potential_32',
        'battery_percent', 
        'thermocouple_1_temp', 'thermocouple_2_temp'
               ]
    
    # widgets = {
    #    'comment':     Textarea(attrs={'rows':2, 'cols':20}),
    #    'description': Textarea(attrs={'rows':2, 'cols':20}),
    #    'date':        TextInput(attrs={'width':10, 'class':'hasDatePicker'}),
    #    }


    def getProbes(self, user):
        return Probe.objects.filter( Q(field_list__farm__farmer=user) | 
                                 Q(field_list__farm__users=user)).distinct()

    def getProbeCodes(self, user):
        probes = self.getProbes(user)
        codes = map(lambda p: (p.farm_code, p.probe_code),  probes)
        return codes

    def get_queryset(self):
        user = self.request.user
        queryset = super(ProbeReadingFormsetView, self).get_queryset()


        query = Q()
        for codepair in self.getProbeCodes(user):
            query = query | Q( farm_code=codepair[0], probe_code=codepair[1] )

        queryset = queryset.filter(query ).distinct()
        
        return queryset.distinct()

    def get_factory_kwargs(self):
        kwargs = super(ProbeReadingFormsetView, self).get_factory_kwargs()
        if hasattr(self, 'widgets'):
            kwargs[ 'widgets' ] = self.widgets
        return kwargs



class ProbeReadingListView(ListView):
    model = ProbeReading
    template_name = 'farms/probe_reading_list.html'
    fields = [ 
        'farm_code', 'probe_code', 
        'reading_datetime',
        'soil_potential_8', 'soil_potential_16', 'soil_potential_32',
        'battery_percent', 
        'thermocouple_1_temp', 'thermocouple_2_temp'
               ]
    context_object_name = 'object_list'
    
    # widgets = {
    #    'comment':     Textarea(attrs={'rows':2, 'cols':20}),
    #    'description': Textarea(attrs={'rows':2, 'cols':20}),
    #    'date':        TextInput(attrs={'width':10, 'class':'hasDatePicker'}),
    #    }


    def getProbes(self, user):
        return Probe.objects.filter( Q(field_list__farm__farmer=user) | 
                                 Q(field_list__farm__users=user)).distinct()

    def getProbeCodes(self, user):
        probes = self.getProbes(user)
        codes = map(lambda p: (p.farm_code, p.probe_code),  probes)
        return codes

    def get_queryset(self):
        user = self.request.user
        queryset = super(ProbeReadingListView, self).get_queryset()


        query = Q()
        for codepair in self.getProbeCodes(user):
            query = query | Q( farm_code=codepair[0], probe_code=codepair[1] )

        queryset = queryset.filter(query ).distinct()
        
        return queryset.distinct()

    def get_factory_kwargs(self):
        kwargs = super(ProbeReadingListView, self).get_factory_kwargs()
        if hasattr(self, 'widgets'):
            kwargs[ 'widgets' ] = self.widgets
        return kwargs






