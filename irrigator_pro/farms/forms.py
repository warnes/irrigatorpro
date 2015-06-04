from django.forms import ModelForm
from django.forms.models import BaseModelFormSet
from django.forms.models import inlineformset_factory, modelformset_factory
from django.forms import Textarea
from farms.models import Farm, Field, CropSeason, CropSeasonEvent, Probe
from common.models import Audit, Comment, Location, NameDesc
from django.contrib.auth.models import User


class FarmForm(ModelForm):
    class Meta:
        model = Farm
        fields = ['farmer',
                  'name',
                  'description',
#                  'users',
                  'address_1',
                  'address_2',
                  'city',
                  'county',
                  'state',
                  'zipcode',
                  'gps_latitude', 
                  'gps_longitude'
              ]


        # From: http://stackoverflow.com/questions/6541477/ordering-choices-in-modelform-manytomanyfield-django
        # Doesn't look like it's used at all
    def __init__(self, *args, **kwargs):
        super(FarmForm, self).__init__(*args, **kwargs)   
#        self.fields['users'].queryset = User.objects.all().order_by('last_name')
        


FieldFormSet = inlineformset_factory(Farm, 
                                     Field, 
                                     fields=[
                                         'name',
                                         'description',
                                         'acres',
                                         'soil_type',
                                         'irr_capacity',
                                     ],
                                     widgets = {
                                         'description': Textarea(attrs={'rows':2, 
                                                                        'cols':20}),
                                     }
                                    )



### Define a form for the probe in order to redefine the 
### validation method.
# class ProbeForm(ModelForm):
#     class Meta:
#         model = Probe
#         fields = [ 'field_list', ] \
#                  + NameDesc.fields \
#                  + [ 'radio_id'] \
#                  + Comment.fields
#         widgets = {
#             'description': Textarea(attrs={'rows':2, 
#                                            'cols':20}),
#         }


#     ###
#     ### Redefine is_valid to issue an error if the id is used in a different field with
#     ### an overlapping crop season.

#     def is_valid(self):
#         valid = super(ProbeForm, self).is_valid()
#         print 'instance: ', self.instance
#         return False
#         if valid is False:
#             return False


#         probes_query = Probe.objects.filter(radio_id = self.cleaned_data['radio_id'])
#         if len(probes_query) == 0: return True


# #        for other_probe in probes_query:
#            if other_

class BaseProbeFormSet(BaseModelFormSet):
    def clean(self):
        if any(self.errors):
            print "Found errors in basic form. Don't bother more"
            return

        print 'No error found'
        for form in self.forms:
            print "Looking at form: ", form


#ProbeFormFormSet = modelformset_factory(Probe, formset=BaseProbeFormSet)

CropSeasonEventFormSet = inlineformset_factory(CropSeason, 
                                             CropSeasonEvent, 
                                             fields = [ 'crop_event',
                                                        'date',
                                                    ],
                                             widgets = {
                                                 'description': Textarea(attrs={'rows':2, 
                                                                                'cols':20}),
                                             }
                                         )
