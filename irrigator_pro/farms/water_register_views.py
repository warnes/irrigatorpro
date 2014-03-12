from django.shortcuts import get_object_or_404, redirect, render, render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.db.models import Q

from farms.models import CropSeason, Field, WaterRegister


class WaterRegisterListView(ListView):
    template_name = "farms/water_register_list.html"
    model = WaterRegister
    fields = [ 'crop_season',
               'field',
               'date',
               'crop_stage',
               'daily_water_use',
               'rain',
               'irrigation',
               'average_water_content',
               'computed_from_probes',
               'irrigate_flag',
               'check_sensors_flag',
             ]

    def get_queryset(self):
        queryset = WaterRegister.objects.filter(crop_season=self.crop_season,
                                                field=self.field)

        if not queryset.count():
            return queryset

        field = queryset[0].field
        farm = field.farm

        farmer = farm.farmer
        users  = farm.users.all()
        user_list = [ x for x in  users ]
        user_list.append(farmer)

        if not self.request.user in user_list:
            redirect( reverse('home') )

        return queryset.distinct()

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.crop_season = kwargs.get('season', None)
        self.field       = kwargs.get('field', None)

        return super(WaterRegisterListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(WaterRegisterListView, self).get_context_data(**kwargs)
        context['crop_season'] = CropSeason.objects.get(pk=int(self.crop_season))
        context['field']       = Field.objects.get(pk=int(self.field))
        return context

