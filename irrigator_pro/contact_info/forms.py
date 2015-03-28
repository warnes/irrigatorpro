from django.shortcuts import render
from django.forms import ModelForm
from common.models import Audit, Comment, Location, NameDesc
from contact_info.models import Contact_Info

class Contact_InfoForm(ModelForm):
    class Meta:
        model=Contact_Info
        fields = Location.fields \
                 + [ 'phone', 'fax' ]
                 

    
