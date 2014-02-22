from extra_views import InlineFormSet, CreateWithInlinesView, ModelFormSetView, UpdateWithInlinesView
from django.forms import Textarea, MultipleChoiceField
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.views.generic.list import ListView

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from farms.models import Farm, Field, Planting, PlantingEvent, Probe


def plantings_filter(user):
        return Planting.objects.filter( Q(farm__farmer=user) |
                                        Q(farm__users=user) ).distinct()

def fields_filter(user):
        return Field.objects.filter( Q(farm__farmer=user) |
                                     Q(farm__users=user) ).distinct()
        
def farms_filter(user):
        return Farm.objects.filter( Q(farmer=user) |
                                    Q(users=user) ).distinct()



planting_fields = ('name',
                   'description',
                   'crop',
                   'planting_date',
                   'farm',
                   'field_list',
                   'comment'
                   ) 


class PlantingListView(ListView):
    template_name = "farms/planting_list.html"
    model = Planting
    fields = planting_fields
    
    context_object_name = 'planting_list'

    def get_queryset(self):
        return plantings_filter(self.request.user)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PlantingListView, self).dispatch(*args, **kwargs)



class PlantingEventsInline(InlineFormSet):
    model = PlantingEvent
    can_delete=False
    fields = [ 'crop_event',
               'date',
             ]
    readonly_fields = [ 'crop_event' ] #!# not implemented respected
    extra = 0 
    
    def get_factory_kwargs(self):
        kwargs = super(PlantingEventsInline, self).get_factory_kwargs()
        kwargs[ 'extra' ] = self.extra
        return kwargs
        
    def get_readonly_fields(self):
        return readonly_fields


class PlantingUpdateView(UpdateWithInlinesView):
    model = Planting
    fields = planting_fields
    inlines = [ PlantingEventsInline ]
    template_name = 'farms/planting_and_planting_events.html'

    def get_success_url(self):
        return reverse('planting_id', args=[self.object.pk])

    def get_queryset(self):
        user = self.request.user
        queryset = super(PlantingUpdateView, self).get_queryset()

        queryset = queryset.filter( Q(farm__farmer=user) | 
                                    Q(farm__users=user) 
                                  )
        
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super(PlantingUpdateView, self).get_context_data(**kwargs)
        context['planting_list'] = plantings_filter(self.request.user)
        return context

    def get_form(self, *args, **kwargs):
        form = super(PlantingUpdateView, self).get_form(*args, **kwargs)
        form.fields["farm"].queryset       = farms_filter(self.request.user)
        form.fields["field_list"].queryset = fields_filter(self.request.user)
        return form



class PlantingCreateView(CreateWithInlinesView):
    model = Planting
    fields = planting_fields
    inlines = [ PlantingEventsInline ]
    template_name = 'farms/planting_and_planting_events.html'

    def get_success_url(self):
        return reverse('planting_id', args=[self.object.pk])

    def get_queryset(self):
        user = self.request.user
        queryset = super(PlantingCreateView, self).get_queryset()

        queryset = queryset.filter( Q(farm__farmer=user) | 
                                    Q(farm__users=user) 
                                  )
        
        return queryset.distinct()

    def get_factory_kwargs(self):
        kwargs = super(PlantingEventsInline, self).get_factory_kwargs()
        #kwargs[ 'widgets' ] = self.widgets
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(PlantingCreateView, self).get_context_data(**kwargs)
        context['planting_list'] = plantings_filter(self.request.user)
        return context

    def get_form(self, *args, **kwargs):
        form = super(PlantingCreateView, self).get_form(*args, **kwargs)
        form.fields["farm"].queryset       = farms_filter(self.request.user)
        form.fields["field_list"].queryset = fields_filter(self.request.user)
        return form




