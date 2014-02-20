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

class FarmMixin:
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = self.get_object()

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        field_form = FieldFormSet(prefix='field')

           
        field_form_headers = map(lambda field: field.label,
                                 field_form[0])
        field_form_headers = filter(lambda label: not label in ( 'Id', 'Farm' ),
                                    field_form_headers)

        context = self.get_context_data(form=form,
                                        field_form=field_form,
                                        field_form_headers=field_form_headers,
                                    )
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = self.get_object()

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        field_form = FieldFormSet(self.request.post, prefix='field')
        if (form.is_valid() and field_form.is_valid() ):
            return self.form_valid(form, field_form)
        else:
            return self.form_invalid(form, field_form)

    def form_valid(self, form, field_form):
        """
        Called if all forms are valid. Creates a Farm instance along with
        associated Fields and then redirects to a success page.
        """
        self.object = form.save()
        field_form.instance = self.object
        field_form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, ingredient_form, instruction_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        context = self.get_context_data(form=form,
                                        field_form=field_form)
        return self.render_to_response(context)


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


class FarmUpdateView(FarmMixin, UpdateView):
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


class FarmCreateView(FarmMixin, CreateView):
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

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FarmCreateView, self).dispatch(*args, **kwargs)
    
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

    # def get(self, request, *args, **kwargs):
    #     """
    #     Handles GET requests and instantiates blank versions of the form
    #     and its inline formsets.
    #     """
    #     self.object = None
    #     form_class = self.get_form_class()
    #     form = self.get_form(form_class)
    #     field_form = FieldFormSet(prefix='field')

           
    #     field_form_headers = map(lambda field: field.label,
    #                              field_form[0])
    #     field_form_headers = filter(lambda label: not label in ( 'Id', 'Farm' ),
    #                                 field_form_headers)

    #     context = self.get_context_data(form=form,
    #                                     field_form=field_form,
    #                                     field_form_headers=field_form_headers,
    #                                 )
    #     return self.render_to_response(context)

    # def post(self, request, *args, **kwargs):
    #     """
    #     Handles POST requests, instantiating a form instance and its inline
    #     formsets with the passed POST variables and then checking them for
    #     validity.
    #     """
    #     self.object = None
    #     form_class = self.get_form_class()
    #     form = self.get_form(form_class)
    #     field_form = FieldFormSet(self.request.post, prefix='field')
    #     if (form.is_valid() and field_form.is_valid() ):
    #         return self.form_valid(form, field_form)
    #     else:
    #         return self.form_invalid(form, field_form)

    # def form_valid(self, form, field_form):
    #     """
    #     Called if all forms are valid. Creates a Farm instance along with
    #     associated Fields and then redirects to a success page.
    #     """
    #     self.object = form.save()
    #     field_form.instance = self.object
    #     field_form.save()
    #     return HttpResponseRedirect(self.get_success_url())

    # def form_invalid(self, form, ingredient_form, instruction_form):
    #     """
    #     Called if a form is invalid. Re-renders the context data with the
    #     data-filled forms and errors.
    #     """
    #     context = self.get_context_data(form=form,
    #                                     field_form=field_form)
    #     return self.render_to_response(context)


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


