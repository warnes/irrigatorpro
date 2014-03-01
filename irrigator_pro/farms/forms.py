from django.forms import ModelForm
from django.forms.models import inlineformset_factory, modelformset_factory
from django.forms import Textarea
from farms.models import Farm, Field, CropSeason, CropSeasonEvent, Probe
from common.models import Audit, Comment, Location, NameDesc

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


ProbeFormSet = modelformset_factory(Probe,
                                    fields = [ 'field_list', ] \
                                             + NameDesc.fields \
                                             + [ 'radio_id'] \
                                             + Comment.fields,
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
