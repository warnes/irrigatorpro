from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from django.forms import Textarea
from farms.models import Farm, Field

class FarmForm(ModelForm):
    class Meta:
        model = Farm

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
