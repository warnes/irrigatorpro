
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse, reverse_lazy

from django.forms.models import BaseModelForm
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator

from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView

from farms.readonly import ReadonlyFormset
from farms.models import Farm, InvitedUser

from contact_info.forms import Contact_InfoForm
from contact_info.models import Contact_Info, SMS_Info

from twilio.util import RequestValidator
from twilio.rest import TwilioRestClient

from irrigator_pro.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER

import json
import re
from phone_number import PhoneNumber


class SMSException(Exception):

    def __init__(self, m):
        self.msg = m


# Comment to see if it is used.
#class Contact_InfoCreateView(CreateView):
#    model = Contact_Info

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
                      'mobile': self.get_mobile_number()
                })


    # TODO Clean form manually, instead of using is_valid(), so we don't have to 
    # duplicate code

    def post (self, request, *args, **kwargs):

        form = Contact_InfoForm(request.POST, instance = self.get_object())
        mobile_number = request.POST.get("mobile")
        if form.is_valid():
            try:
                smsInfoObject = self.get_sms_object(request, mobile_number)
                form.save()
                # We have validated that the phone numbers are valid. We need
                # manually save the mobile number (not in the form) as well as 
                # phone and fax to be in the format we desire.


                ob = self.get_object();
                self.object = ob
                print 'original', ob.phone

                phone = PhoneNumber(ob.phone)
                fax = PhoneNumber(ob.fax)
                ob.sms_info = smsInfoObject
                ob.phone = phone.unformatted
                ob.fax = fax.unformatted

                ob.save()
                print 'after change', self.object.phone

                form = Contact_InfoForm(instance = ob)
                return render(request, self.template_name, {
                    'form': form,
                    'user': self.request.user,
                    'mobile': self.get_mobile_number()
                })
            


            except SMSException as e:
                return render(request, self.template_name, {
                    'form': form, 
                    'user': self.request.user,
                    'sms_error': e.msg,
                    'mobile': request.POST.get("mobile")
                })

        else:
            # Form is not valid. May still want to give a message if 
            # the format is not valid, or number already exists
            sms_err = ""
            try:
                smsInfoObject = self.get_sms_object(request, mobile_number)
            except SMSException as e:
                sms_err = e.msg
                
            return render(request, self.template_name, {
                'form': form,
                'sms_error': sms_err,
                'user': self.request.user,
                'mobile': request.POST.get("mobile")
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

    def get_mobile_number(self):
        o = self.get_object();
        if o.sms_info is not None:
            return o.sms_info.number
        return ""


    def get_sms_object(self, request, mobile_number):

        sms = PhoneNumber(mobile_number)
        if not sms.valid:
            raise SMSException(sms.error_msg)

        try:
            sms_object = SMS_Info.objects.get(number = sms.unformatted)

            try:
                ci = Contact_Info.objects.get(sms_info = sms_object)
                if ci == self.get_object():
                    return sms_object
                else:
                    raise SMSException('This number is already used by someone else.')    
            except ObjectDoesNotExist:
                return sms_object

        except ObjectDoesNotExist:
            o = SMS_Info(number = sms.unformatted)
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

def send_sms(sms_info):

    body = "Activation message for Irrigator Pro. If you did not initialize the process just ignore this message. Otherwise reply with OK as the message."
    client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(body=body,
                                     to="+1" + sms_info.number, # Replace with your phone number
                                     from_= TWILIO_PHONE_NUMBER) # Replace with your Twilio number
    print message.sid




## This method normally invoke through ajax

def validate_sms(request):
    contact_info = Contact_Info.objects.get(user = request.user)
    if contact_info is None:
        print 'Validating for non-existing user???'
        HttpResponseForbidden()

    sms_info = contact_info.sms_info
    if sms_info is None or sms_info.status != "New":
        print 'Validating for non-existing sms, or non-new sms!!!'
        HttpResponseForbidden()
        
    # Should probably check if the sms was correctly sent
#    send_sms(sms_info)
    sms_info.status = "Submitted"
    sms_info.save()
    return HttpResponse('Nothing')


## This method normally invoke through ajax
## Will list all the existing users that are not already listed as authorized users, 
## plus those that are pending an invitation.
# example from http://flaviusim.com/blog/AJAX-Autocomplete-Search-with-Django-and-jQuery/
# def get_drugs(request):
#     if request.is_ajax():
#         q = request.GET.get('term', '')
#         drugs = Drug.objects.filter(short_name__icontains = q )[:20]
#         results = []
#         for drug in drugs:
#             drug_json = {}
#             drug_json['id'] = drug.rxcui
#             drug_json['label'] = drug.short_name
#             drug_json['value'] = drug.short_name
#             results.append(drug_json)
#         data = json.dumps(results)
#     else:
#         data = 'fail'
#     mimetype = 'application/json'
#     return HttpResponse(data, mimetype)

def get_available_users(request, **kwargs):
    if request.is_ajax():
        q = request.GET.get('term', '')
        all_users = User.objects.filter(email__icontains = q)
        invited_users = InvitedUser.objects.filter(email__icontains = q)
        
        farm = Farm.objects.get(pk=kwargs['farm_pk'])

        emails =  map(lambda x: x.email, set(all_users)     - set(farm.users.all()) )
        emails += map(lambda x: x.email, set(invited_users) - set(farm.users.all()) )
        results = []
        for e in emails:
            e_json = {}
            e_json['id'] = e
            e_json['label'] = e
            e_json['value'] = e
            results.append(e_json)
        data = json.dumps(results)
        
    else:
        data = 'fail'

    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


## Validation, copied from
## http://codehighway.postach.io/post/twilio-sms-receive-crazy-simple


def validate_request(request):
    """
    Make sure the request is from Twilio and is valid.
    Ref: https://www.twilio.com/docs/security#validating-requests
    """

    # Forgot where this token if from. Different from above.
    # From: https://www.twilio.com/user/account/developer-tools/test-credentials
    # Should probably use TWILIO_AUTH_TOKEN once testing complete.
    auth_token = '9ea8a4f0ac5fd659fef71719e480c3c0'
    if 'HTTP_X_TWILIO_SIGNATURE' not in request.META:
        return 'X_TWILIO_SIGNATURE header is missing ' \
            'from request, not a valid Twilio request.'
        
        validator = RequestValidator(auth_token)
        
        if not validator.validate(
                request.build_absolute_uri(), 
                request.POST, 
                request.META['HTTP_X_TWILIO_SIGNATURE']):
            return 'Twilio request is not valid.'

        
@csrf_exempt
def incoming_sms(request):

    bad_request_message = validate_request(request)
    if bad_request_message:
        print bad_request_message
        return HttpResponseForbidden()

    body = request.POST['Body']
    # Right now only handle North American numbers. We receive them as
    # +15555555555. Will just remove first 2 characters
    sender_number = request.POST['From'][2:]

    sms_rec = SMS_Info.objects.get(number = sender_number)
    if sms_rec is None or sms_rec.status != "Submitted":
        print sender_number, ' not in database, or not in submitted status.'
        return HttpResponseForbidden()
        
    if body.upper().strip() != "OK":
        print sender_number, " will be set to denied. Received a non OK response"
        sms_rec.status = "Denied"
    else:
        print sender_number, " validated"
        sms_rec.status = "Validated"
    
    sms_rec.save(force_update=True)
    return HttpResponse('Nothing')
