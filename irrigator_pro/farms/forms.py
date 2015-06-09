from django.forms import ModelForm
from django.forms.models import BaseModelFormSet
from django.forms.models import inlineformset_factory, modelformset_factory
from django.forms import Textarea
from farms.models import Farm, Field, CropSeason, CropSeasonEvent, Probe, WaterHistory
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
