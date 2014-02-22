from extra_views import ModelFormSetView
from django.forms import Textarea, MultipleChoiceField
from django.db.models import Q

from farms.models import Probe
from common.models import Audit, Comment, Location, NameDesc

from farm_views import *


class ProbesView(ModelFormSetView):
    model = Probe

    template_name = 'farms/formset.html'

    fields = [ 'farm', 'field_list', ] \
             + ['name' ] \
             + [ 'farm_code', 'probe_code'] 

    can_delete=True
 
    def get_queryset(self):
        user = self.request.user
        queryset = super(ProbesView, self).get_queryset()

        queryset = queryset.filter( Q(farm__farmer=user) | 
                                    Q(farm__users=user) 
                               )
        
        return queryset.distinct()


    
