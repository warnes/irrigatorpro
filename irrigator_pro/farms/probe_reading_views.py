from extra_views import ModelFormSetView
from django.forms import Textarea, TextInput
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.forms.widgets import HiddenInput

from farms.models import CropSeason, Field, Probe, ProbeReading

class ProbeReadingEmptyView(TemplateView):
    template_name = 'farms/probe_readings_empty.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProbeReadingEmptyView, self).dispatch(*args, **kwargs)

class ProbeReadingFormsetView(ModelFormSetView):
    model = ProbeReading
    template_name = 'farms/probe_readings.html'
    fields = [
        'datetime',
        'radio_id',
        'soil_potential_8', 'soil_potential_16', 'soil_potential_24',
        'battery_percent',
        'thermocouple_1_temp', 'thermocouple_2_temp'
             ]
    widgets = {
        'radio_id': HiddenInput()
        }
    can_delete = True

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.season = CropSeason.objects.get(pk=kwargs.get('season', None))
        self.field  = Field.objects.get(pk=kwargs.get('field', None))
        return super(ProbeReadingFormsetView, self).dispatch(*args, **kwargs)

    def getProbes(self, user, season, field):
        probes = Probe.objects.filter( Q(field__farm__farmer=user) |
                                     Q(field__farm__users=user)
                                   )
        if season:
            probes = probes.filter( crop_season = season )
        if field:
            probes = probes.filter( field_list = field )
        return probes.distinct()

    def getRadioIds(self, user, season, field):
        probes = self.getProbes(user, season, field)
        radio_ids = map(lambda p: p.radio_id,  probes)
        return radio_ids

    def get_queryset(self):
        user = self.request.user
        queryset = super(ProbeReadingFormsetView, self).get_queryset()

        query = Q()
        radioIds = self.getRadioIds(user, self.season, self.field)
        if len(radioIds) < 1:
            query = query | Q( radio_id="" )
        else:
            for radio_id in radioIds:
                query = query | Q( radio_id=radio_id )

        queryset = queryset.filter(query).distinct().order_by('radio_id','datetime')

        if self.season:
            crop_season = CropSeason.objects.get(pk=self.season.pk)
            queryset = queryset.filter( datetime__gte=crop_season.season_start_date,
                                        datetime__lte=crop_season.season_end_date )


        return queryset.distinct()

    def get_factory_kwargs(self):
        kwargs = super(ProbeReadingFormsetView, self).get_factory_kwargs()
        if hasattr(self, 'widgets'):
            kwargs[ 'widgets' ] = self.widgets
        return kwargs
        
    def get_extra_form_kwargs(self):
        kwargs = super(ProbeReadingFormsetView, self).get_extra_form_kwargs()
        self.radio_id = self.getRadioIds(self.request.user, self.season, self.field)[0]
        kwargs['initial'] = { 'radio_id': self.radio_id }
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ProbeReadingFormsetView, self).get_context_data(**kwargs)
        context['season'] = self.season
        context['field'] = self.field
        context['radio_id'] = self.radio_id
        return context
        
