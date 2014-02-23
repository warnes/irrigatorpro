from extra_views import InlineFormSet, CreateWithInlinesView, ModelFormSetView, UpdateWithInlinesView
from django.forms import Textarea, MultipleChoiceField
from django.db.models import Q
from django.core.urlresolvers import reverse

from farms.models import Probe, WaterHistory

from farm_views import *
from planting_views import *

class ProbesView(ModelFormSetView):
    model = Probe

    template_name = 'farms/probe_list.html'

    fields = [ 'name', 'farm', 'field_list', 'farm_code', 'probe_code'] 

    can_delete=True
 
    def get_queryset(self):
        user = self.request.user
        queryset = super(ProbesView, self).get_queryset()

        queryset = queryset.filter( Q(farm__farmer=user) | 
                                    Q(farm__users=user) 
                                  )
        
        return queryset.distinct()


class WaterHistoryView(ModelFormSetView):
    model = WaterHistory

    template_name = 'farms/formset.html'

    fields = [ 'farm', 'field_list', 'date', 'rain', 'irrigation', 'comment' ]

    can_delete=True
 
    def get_queryset(self):
        user = self.request.user
        queryset = super(WaterHistoryView, self).get_queryset()

        queryset = queryset.filter( Q(farm__farmer=user) | 
                                    Q(farm__users=user) 
                                  )
        
        return queryset.distinct()


