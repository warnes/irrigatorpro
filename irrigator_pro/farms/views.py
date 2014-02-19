from django.shortcuts import get_object_or_404, redirect, render, render_to_response
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.db.models import Q

#from farms.forms import FarmForm
from farms.models import Farm

from sys import stderr

class FarmListView(ListView):
    template_name = "farms/farm_list.html"
    model = Farm
    fields = ('farmer',
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

    context_object_name = 'farm_list'


    def get_context_data(self, **kwargs):
        context = super(FarmListView, self).get_context_data(**kwargs)
        #context['farm_list'] = Farm.objects.filter( Q(farmer=self.request.user) |
        #                                            Q(users=self.request.user) ).distinct()
        context['farm_path'] = '/farm/'
        return context


    def get_queryset(self):
        return Farm.objects.filter( Q(farmer=self.request.user) |
                                    Q(users=self.request.user) ).distinct()

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FarmListView, self).dispatch(*args, **kwargs)


class FarmUpdateView(UpdateView):
    template_name = "farms/farm_and_fields.html"
    model = Farm
    pk_field = 'pk' 
    fields = ('farmer',
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

    def get_success_url(self):
        path = self.request.path.replace('new', "%s" % self.object.pk)
        print path
        return path

    def get_context_data(self, **kwargs):
        context = super(FarmUpdateView, self).get_context_data(**kwargs)
        context['farm_list'] = Farm.objects.filter( Q(farmer=self.request.user) |
                                                    Q(users=self.request.user) ).distinct()
        context['farm_path'] = '/farm/'
        return context


    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FarmUpdateView, self).dispatch(*args, **kwargs)


class FarmCreateView(CreateView):
    template_name = "farms/farm_and_fields.html"
    model = Farm
    pk_field = 'pk' 
    fields = ('farmer',
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
    
    def get_success_url(self):
        path = self.request.path.replace('new', "%s" % self.object.pk)
        print path
        return path

    def get_initial(self):
        dict = super(FarmCreateView, self).get_initial()
        dict['farmer'] = self.request.user
        return dict
        
    def get_context_data(self, **kwargs):
        context = super(FarmCreateView, self).get_context_data(**kwargs)
        context['farm_list'] = Farm.objects.filter( Q(farmer=self.request.user) |
                                                    Q(users=self.request.user) ).distinct()
        context['farm_path'] = '/farm/'
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FarmCreateView, self).dispatch(*args, **kwargs)



class FarmDeleteView(DeleteView):
    template_name = "farms/farm_delete.html"
    model = Farm
    pk_field = 'pk' 
    fields = ('farmer',
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
    
    success_url = "/farm/"

    def get_context_data(self, **kwargs):
        context = super(FarmDeleteView, self).get_context_data(**kwargs)
        context['farm_list'] = Farm.objects.filter( Q(farmer=self.request.user) |
                                                    Q(users=self.request.user) ).distinct()
        context['farm_path'] = '/farm/'
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FarmDeleteView, self).dispatch(*args, **kwargs)


