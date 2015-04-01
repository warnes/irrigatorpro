from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist

from django.views.decorators.csrf import csrf_exempt

from farms.readonly import ReadonlyFormset
from contact_info.forms import Contact_InfoForm
from contact_info.models import Contact_Info, SMS_Info

from twilio.util import RequestValidator
from twilio.rest import TwilioRestClient

from irrigator_pro.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER

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
        

        p = re.compile('^[\d\s()-]+$')
        if not p.match(mobile_number) :
            raise SMSException("The number can only contain numbers, the - sign, and ()")

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

def send_sms(sms_info):

    body = "Activation message for Irrigator Pro. If you did not initialize the process just ignore this message. Otherwise reply with OK as the message."
    client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(body=body,
                                     to="+1" + sms_info.number, # Replace with your phone number
                                     from_= TWILIO_PHONE_NUMBER) # Replace with your Twilio number
    print message.sid




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
    send_sms(sms_info)
    sms_info.status = "Submitted"
    sms_info.save()
    return HttpResponse('Nothing')



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
        
    print sms_rec.muser
    if body.upper().strip() != "OK":
        print sender_number, " will be set to denied. Received a non OK response"
        sms_rec.status = "Denied"
    else:
        print sender_number, " validated"
        sms_rec.status = "Validated"
    
    print sms_rec.muser
    sms_rec.save(force_update=True)
    return HttpResponse('Nothing')
