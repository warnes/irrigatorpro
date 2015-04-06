from django.shortcuts import render
from django.forms import ModelForm
from common.models import Audit, Comment, Location, NameDesc
from contact_info.models import Contact_Info

from phone_number import PhoneNumber

    
class Contact_InfoForm(ModelForm):
    class Meta:
        model=Contact_Info
        fields = Location.fields \
                 + [ 'phone', 'fax' ]
                 

    
    # Define own validation. Takes the default, but also verify the the phone and fax numbers
    # are valid

    # May add validation of zip code.
    def is_valid(self):

        valid = super(Contact_InfoForm, self).is_valid()

        phone = PhoneNumber(self.cleaned_data['phone'])
        fax = PhoneNumber(self.cleaned_data['fax'])

        if not phone.valid:
            valid = False
            del self.cleaned_data['phone']
            self._errors['phone'] = phone.error_msg

        if not fax.valid:
            valid = False
            del self.cleaned_data['fax']
            self._errors['fax'] = fax.error_msg
            
        return valid
