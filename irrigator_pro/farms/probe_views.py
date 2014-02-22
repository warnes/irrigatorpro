from django.shortcuts import get_object_or_404, redirect, render, render_to_response
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.db.models import Q
from farms.forms import FieldFormSet

#from farms.forms import FarmForm
from farms.models import Farm

from sys import stderr

class ProbeListView(ListView):
    template_name = "probes/probe_list.html"
    model = Probe
    fields = ('probeer',
              'name',
              'description',
              'users',
              'address_1',
              'address_2',
              'city',
              'county',
              'state',
              'zipcode',
               )

    context_object_name = 'probe_list'


    def get_context_data(self, **kwargs):
        context = super(ProbeListView, self).get_context_data(**kwargs)
        context['probe_path'] = '/probe/'
        return context


    def get_queryset(self):
        return Probe.objects.filter( Q(probeer=self.request.user) |
                                    Q(users=self.request.user) ).distinct()

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProbeListView, self).dispatch(*args, **kwargs)

