from django.shortcuts import get_object_or_404, redirect, render, render_to_response
from extra_views import InlineFormSet, CreateWithInlinesView, ModelFormSetView, UpdateWithInlinesView
from django.forms import Textarea, MultipleChoiceField
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.views.generic.list import ListView

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from farms.models import Farm, Field, Planting, PlantingEvent, Probe
from farms.readonly import ReadonlyFormset

def plantings_filter(user):
        return Planting.objects.filter( Q(field_list__farm__farmer=user) |
                                        Q(field_list__farm__users=user) ).distinct()

def fields_filter(user):
        return Field.objects.filter( Q(farm__farmer=user) |
                                     Q(farm__users=user) ).distinct()
        

planting_fields = ('name',
                   'description',
                   'crop',
                   'planting_date',
                   'field_list',
                   'comment'
                   ) 


class PlantingListView(ListView):
    template_name = "farms/planting_list.html"
    model = Planting
    fields = planting_fields

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
    extra = 0 
    
    def get_factory_kwargs(self):
        kwargs = super(PlantingEventsInline, self).get_factory_kwargs()
        kwargs[ 'extra' ] = self.extra
        return kwargs
        

class PlantingEventsInlineReadonly(ReadonlyFormset, PlantingEventsInline):
    class NewMeta:
            readonly = [ 'crop_event' ]


class PlantingUpdateView(UpdateWithInlinesView):
    model = Planting
    fields = planting_fields
    inlines = [ PlantingEventsInlineReadonly ]
    template_name = 'farms/planting_and_planting_events.html'

    planting_list = None

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """
        This function ensures that the user has the right to access
        this object by comparing the primary key of this object to the
        list of primary keys constructed from a query of objects where
        this user is either the farmer or the one of the users.
        """
        self.planting_list = plantings_filter(self.request.user)
        user_pk = int(kwargs['pk'])
        pk_list = map( lambda x: int(x.pk), self.planting_list )
        if not user_pk in pk_list:
            return redirect( reverse('planting_list') )
        else:
            return super(PlantingUpdateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('planting_id', args=[self.object.pk])

    def get_queryset(self):
        user = self.request.user
        queryset = super(PlantingUpdateView, self).get_queryset()

        queryset = queryset.filter( Q(field_list__farm__farmer=user) | 
                                    Q(field_list__farm__users=user) 
                                  )
        
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super(PlantingUpdateView, self).get_context_data(**kwargs)
        context['planting_list'] = self.planting_list
        return context

    def get_form(self, *args, **kwargs):
        """
        Ensure that the "Field List" widget only shows fields that correspind to this user
        """
        form = super(PlantingUpdateView, self).get_form(*args, **kwargs)
        form.fields["field_list"].queryset = fields_filter(self.request.user)
        return form



class PlantingCreateView(CreateWithInlinesView):
    model = Planting
    fields = planting_fields
    inlines = [ PlantingEventsInline ]
    template_name = 'farms/planting_and_planting_events.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PlantingCreateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('planting_id', args=[self.object.pk])

    def get_queryset(self):
        user = self.request.user
        queryset = super(PlantingCreateView, self).get_queryset()

        queryset = queryset.filter( Q(field_list__farm__farmer=user) | 
                                    Q(field_list__farm__users=user) 
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
        form.fields["field_list"].queryset = fields_filter(self.request.user)
        return form



class PlantingDeleteView(DeleteView):
    template_name = "farms/planting_delete.html"
    model = Planting
    pk_field = 'pk' 
    
    success_url = reverse_lazy('planting_list')

    planting_list = None

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """
        This function ensures that the user has the right to access
        this object by comparing the primary key of this object to the
        list of primary keys constructed from a query of objects where
        this user is either the farmer or the one of the users.
        """
        self.planting_list = plantings_filter(self.request.user)
        user_pk = int(kwargs['pk'])
        pk_list = map( lambda x: int(x.pk), self.planting_list )
        if not user_pk in pk_list:
            return redirect( reverse('planting_list') )
        else:
            return super(PlantingDeleteView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(PlantingDeleteView, self).get_context_data(*args, **kwargs)
        context['planting_list'] = self.planting_list
        return context
