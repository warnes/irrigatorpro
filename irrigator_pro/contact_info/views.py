from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.core.urlresolvers import reverse, reverse_lazy

from farms.readonly import ReadonlyFormset
from contact_info.forms import Contact_InfoForm
from contact_info.models import Contact_Info

class Contact_InfoCreateView(CreateView):
    model = Contact_Info

class Contact_InfoUpdateView(UpdateView):
    template_name = "contact_info/contact_info_form.html"
    fields = (#'user',
              'address_1',
              'address_2',
              'city',
              'county',
              'state',
              'zipcode',
              'phone',
#              'sms_info',
              'fax',
              #'cdate',
              #'mdate',
              #'cuser',
              #'muser',        
          )


    def post (self, request, *args, **kwargs):
        print "Into the contact info post:"

        form = Contact_InfoForm(request.POST, instance = self.get_object())
        if form.is_valid():
            print 'The form is valid!!!'
            form.save()
            return redirect(self.get_success_url())

        return render(request, self.template_name, {
            'form': form
        })



    def get_success_url(self):
        return self.request.path

    def get_object(self):
        (obj, created) = Contact_Info.objects.get_or_create(user = self.request.user, 
                                                            defaults = { 'cuser': self.request.user,
                                                                         'muser': self.request.user,
                                                                       }
                                                           )
        print 'From get onject: ', obj
        return obj

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Contact_InfoUpdateView, self).dispatch(*args, **kwargs)

 
class UserUpdateView(UpdateView):
    template_name = "contact_info/user_info_form.html"
    fields = (
        'first_name',
        'last_name'
    )

    def get_success_url(self):
        return reverse( 'contact_info' )
    
    def get_object(self):
        obj = self.request.user
        return obj

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserUpdateView, self).dispatch(*args, **kwargs)


