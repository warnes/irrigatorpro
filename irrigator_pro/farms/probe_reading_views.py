from extra_views import ModelFormSetView
from django.forms import Textarea, TextInput
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.list import ListView
from django.forms.widgets import HiddenInput

from farms.models import CropSeason, Probe, ProbeReading

class ProbeReadingFormsetView(ModelFormSetView):
    model = ProbeReading
    template_name = 'farms/probe_readings.html'
    fields = [
        'reading_datetime',
        'radio_id',
        'soil_potential_8', 'soil_potential_16', 'soil_potential_24',
        'battery_percent',
        'thermocouple_1_temp', 'thermocouple_2_temp'
             ]
    widgets = {
        'radio_id': HiddenInput()
        }

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.season = kwargs.get('season', None)
        self.field  = kwargs.get('field', None)
        return super(ProbeReadingFormsetView, self).dispatch(*args, **kwargs)

    def getProbes(self, user, season, field):
        probes = Probe.objects.filter( Q(field_list__farm__farmer=user) |
                                     Q(field_list__farm__users=user)
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

        queryset = queryset.filter(query).distinct().order_by('radio_id','reading_datetime')

        if self.season:
            crop_season = CropSeason.objects.get(pk=int(self.season))
            queryset = queryset.filter( reading_datetime__gte=crop_season.season_start_date,
                                        reading_datetime__lte=crop_season.season_end_date )


        return queryset.distinct()

    def get_factory_kwargs(self):
        kwargs = super(ProbeReadingFormsetView, self).get_factory_kwargs()
        if hasattr(self, 'widgets'):
            kwargs[ 'widgets' ] = self.widgets
        return kwargs

