from django.shortcuts import get_object_or_404, redirect, render, render_to_response
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.db.models import Q
from django.core.urlresolvers import reverse, reverse_lazy

from farms.forms import FieldFormSet
from farms.models import Farm

farm_view_fields =  ('farmer',
                     'name',
                     'description',
                     'users',
                     'address_1',
                     'address_2',
                     'city',
                     'county',
                     'state',
                     'zipcode',
                     'gps_latitude', 
                     'gps_longitude'
                 )


def farms_filter(user):
        return Farm.objects.filter( Q(farmer=user) |
                                    Q(users=user) ).distinct()


class FarmMixin:
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = self.get_object()

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        field_form = FieldFormSet(prefix='field', instance=self.object)

           
        field_form_headers = map(lambda field: field.label,
                                 field_form[0])
        field_form_headers = map(lambda label: '' if label in ( 'Delete', 'Id', 'Farm' ) else label,
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
        field_form = FieldFormSet(self.request.POST, prefix='field', instance=self.object)
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
        return redirect(self.get_success_url())

    def form_invalid(self, form, field_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        context = self.get_context_data(form=form,
                                        field_form=field_form)
        return self.render_to_response(context)


class FarmListView(TemplateView):
    template_name = "farms/farm_list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FarmListView, self).dispatch(*args, **kwargs)


class FarmUpdateView(FarmMixin, UpdateView):
    template_name = "farms/farm_and_fields.html"
    model = Farm
    pk_field = 'pk' 
    fields = farm_view_fields

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """
        This function ensures that the user has the right to access
        this object by comparing the primary key of this object to the
        list of primary keys constructed from a query of objects where
        this user is either the farmer or the one of the users.
        """
        farm_list = farms_filter(self.request.user)
        user_pk = int(kwargs['pk'])
        pk_list = map( lambda x: int(x.pk), farm_list )
        if not user_pk in pk_list:
            return redirect( reverse('farm_list') )
        else:
            return super(FarmUpdateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        path = reverse('farm_id', args=[self.object.pk])
        return path


class FarmCreateView(FarmMixin, CreateView):
    template_name = "farms/farm_and_fields.html"
    model = Farm
    pk_field = 'pk' 
    fields = farm_view_fields

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FarmCreateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        path = self.request.path.replace('new', "%s" % self.object.pk)
        return path

    def get_initial(self):
        dict = super(FarmCreateView, self).get_initial()
        dict['farmer'] = self.request.user
        return dict
        
    def get_object(self, queryset=None):
        return None


class FarmDeleteView(DeleteView):
    template_name = "farms/farm_delete.html"
    model = Farm
    pk_field = 'pk' 
    
    success_url = reverse_lazy('farm_list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """
        This function ensures that the user has the right to access
        this object by comparing the primary key of this object to the
        list of primary keys constructed from a query of objects where
        this user is either the farmer or the one of the users.
        """
        farm_list = farms_filter(self.request.user)
        user_pk = int(kwargs['pk'])
        pk_list = map( lambda x: int(x.pk), farm_list )
        if not user_pk in pk_list:
            return redirect( reverse('farm_list') )
        else:
            return super(FarmDeleteView, self).dispatch(*args, **kwargs)





