from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from farms.readonly import ReadonlyFormset
from contact_info.forms import Contact_InfoForm
from contact_info.models import Contact_Info, SMS_Info

import re


class SMSException(Exception):

    def __init__(self, m):
        self.msg = m

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



    def get(self, request, *args, **kwargs):

        self.object = self.get_object()
        form = self.get_form(Contact_InfoForm)


        return render(request, self.template_name, {
                      'form': form,
                      'user': self.request.user,
                      'mobile': self.get_mobile()
                })

    def post (self, request, *args, **kwargs):

        form = Contact_InfoForm(request.POST, instance = self.get_object())
        if form.is_valid():
            mobile_number = request.POST.get("mobile")
            try:
                smsInfoObject = self.get_sms_object(request, mobile_number)
            except SMSException as e:
                return render(request, self.template_name, {
                    'form': form, 
                    'user': self.request.user,
                    'sms_error': e.msg,
                    'mobile': self.get_mobile()
                })

            form.save()

            ob = self.get_object();
            ob.sms_info = smsInfoObject
            ob.save()
            #return redirect(self.get_success_url())
            form.clean()
            return render(request, self.template_name, {
                'form': form,
                'user': self.request.user,
                'mobile': self.get_mobile()
            })
            
        return render(request, self.template_name, {
            'form': form,
            'user': self.request.user,
            'mobile': self.get_mobile()
        })



    def get_success_url(self):
        return self.request.path

    def get_object(self):
        (obj, created) = Contact_Info.objects.get_or_create(user = self.request.user, 
                                                            defaults = { 'cuser': self.request.user,
                                                                         'muser': self.request.user,
                                                                       }
                                                           )
        return obj

    def get_mobile(self):
        o = self.get_object();
        return o.sms_info


    def get_sms_object(self, request, mobile_number):

        if mobile_number.strip() == '':
            return None
        

        p = re.compile('^[\d-]+$')
        if not p.match(mobile_number) :
            raise SMSException("The number can only contain numbers and the - sign")

        p2 = re.compile('[^\d]+')
        m = p2.sub("", mobile_number)
        print m
        if len(m) != 10:
            raise SMSException('Mobile number must contain 10 numbers, preferably in the format 555-555-5555')

        try:
            sms_object = SMS_Info.objects.get(number = m)

            try:
                ci = Contact_Info.objects.get(sms_info = sms_object)
                if ci == self.get_object():
                    return sms_object
                else:
                    raise SMSException('This number is already used by someone else.')    
            except ObjectDoesNotExist:
                return sms_object

        except ObjectDoesNotExist:
            print "This is a new number"
            o = SMS_Info(number = m)
            o.save()
            return o


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



################################################
##### Method to trigger sms validation
###############################################

def validate_sms(request, user_pk):
    print 'Will validate sms'
    return HttpResponse('Nothing')






