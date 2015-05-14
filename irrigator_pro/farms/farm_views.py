from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.core.urlresolvers import reverse, reverse_lazy

from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render, render_to_response
from django.utils.decorators import method_decorator

from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from farms.forms import FarmForm
from farms.forms import FieldFormSet
from farms.models import Farm, InvitedUser
from farms.invited_user_email import send_invitation_email

farm_view_fields =  ('farmer',
                     'name',
                     'description',
#                     'users',
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

        form = self.get_form(FarmForm)

        field_form = FieldFormSet(prefix='field', instance=self.object)
           
        field_form_headers = map(lambda field: field.label,
                                 field_form[0])
        field_form_headers = map(lambda label: '' if label in ( 'Delete', 'Id', 'Farm' ) else label,
                                    field_form_headers)


        # context = self.get_context_data(form=form,
        #                                 field_form=field_form,
        #                                 field_form_headers=field_form_headers
        #                             )
        # context['auth_users'] = self.object.users.all()
        context = self.get_context(form, field_form, field_form_headers)
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

            self.delete_users(request, self.object)
            self.delete_invited_users(request, self.object)
            self.add_users(request, self.object)

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


        field_form_headers = map(lambda field: field.label,
                                 field_form[0])
        field_form_headers = map(lambda label: '' if label in ( 'Delete', 'Id', 'Farm' ) else label,
                                    field_form_headers)


        # context = self.get_context_data(form=form,
        #                                 field_form=field_form,
        #                                 field_form_headers=field_form_headers)
        # context['auth_users'] = self.object.users.all()
        context = self.get_context(form, field_form, field_form_headers)
        return self.render_to_response(context)



    ###
    ## Remove the authorized users.
    ###

    def delete_users(self, request, farm_object):
        deleted_users = request.POST.getlist('deleted_user_auth')
        print "deleted users: ", deleted_users
        if deleted_users is None or len(deleted_users)==0: return
        for u in deleted_users:

            try:
                du = User.objects.get(pk=u)
                farm_object.users.remove(du)
            except:
                raise RuntimeError("Removing non-existing user with pk: " + u)

        farm_object.save()



    ###
    ## Remove the invited users that had been previously saved.
    ###

    def delete_invited_users(self, request, farm_object):
        deleted_users = request.POST.getlist('deleted_user_invited')

        if deleted_users is None or len(deleted_users)==0: return
        for u in deleted_users:

            try:
                du = InvitedUser.objects.get(pk=u)
                du.farms.remove(farm_object)
                du.save()
            except:
                raise RuntimeError("Removing non-existing user with pk: " + pk)





    ###
    ## Add authorized users. The new users are specified by the email, which 
    ## may not be an existing users. In this case look for invited users, or
    ## create a new one,
    ###

    def add_users(self, request, farm_object):

        added_users = request.POST.getlist('added_user')
        print 'Added users: ', added_users

        for u in added_users:
            u = u.strip()
            try:
                user = User.objects.get(email = u)
                farm_object.users.add(user)
                farm_object.save()
            except:
                # User does not exist
                try:
                    invited_user = InvitedUser.objects.get(email = u)
                except:
                    # New user. Must send email
                    send_invitation_email(u, request.user, farm)
                    invited_user = InvitedUser(email = u)
                    invited_user.save()
                print "farm object ", farm_object
                invited_user.farms.add(farm_object)
                invited_user.save()
                


    def get_context(self, form, field_form, field_form_headers):
        context = self.get_context_data(form=form,
                                        field_form=field_form,
                                        field_form_headers=field_form_headers)
        context['auth_users'] = self.object.users.all()
        context['invited_users'] = InvitedUser.objects.filter(farms = self.object).order_by("email")

        print 'Invited users: ', InvitedUser.objects.filter(farms = self.object).order_by("email")

        return context
 
                

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
        print "Getting successurl 1:"
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
        print "Geting successurl 2:"
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





