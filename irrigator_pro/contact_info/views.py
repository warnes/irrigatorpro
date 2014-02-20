from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView

from contact_info.forms import Contact_InfoForm
from contact_info.models import Contact_Info

from sys import stderr

class Contact_InfoCreateView(CreateView):
    model = Contact_Info

@login_required
def edit_contact_info(request):
    cinfo, created = Contact_Info.objects.get_or_create(user=request.user)
    form = Contact_InfoForm(request.POST or None, instance=cinfo)
    if form.is_valid():
        form.save()
        return redirect('/')
    else:
        return render(request, "form.html", {'form': form})

class Contact_InfoDetailView(DetailView):
    template_name = "detail.html"

    def get_object(self):
        obj = Contact_Info.objects.get(user = self.request.user)
        return obj

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Contact_InfoDetailView, self).dispatch(*args, **kwargs)


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
              'mobile',
              'fax',
              #'cdate',
              #'mdate',
              #'cuser',
              #'muser',        
          )

    def get_success_url(self):
        return self.request.path

    def get_object(self):
        obj = Contact_Info.objects.get(user = self.request.user)
        return obj

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Contact_InfoUpdateView, self).dispatch(*args, **kwargs)


class UserDetailView(DetailView):
    template_name = "detail.html"

    fields = (#'user',
              'address_1',
              'address_2',
              'city',
              'county',
              'state',
              'zipcode',
              'phone',
              'mobile',
              'fax',
              #'cdate',
              #'mdate',
              #'cuser',
              #'muser',        
          )
    
    def get_object(self):
        obj = self.request.user
        return obj

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserDetailView, self).dispatch(*args, **kwargs)


