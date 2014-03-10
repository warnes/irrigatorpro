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
from django.forms.models import inlineformset_factory

from farms.models import Farm, Field, CropSeason, CropSeasonEvent, Probe
from farms.readonly import ReadonlyFormset

def crop_seasons_filter(user):
    crop_season_list = CropSeason.objects.filter( Q(field_list__farm__farmer=user) |
                                                  Q(field_list__farm__users=user) ).distinct()
    if crop_season_list:
        return crop_season_list
    else:
        return []

def fields_filter(user):
        return Field.objects.filter( Q(farm__farmer=user) |
                                     Q(farm__users=user) ).distinct()


crop_season_fields = (
                   'name',
                   'description',
                   'crop',
                   'season_start_date',
                   'field_list',
                   'comment'
                   )


class CropSeasonListView(ListView):
    template_name = "farms/crop_season_list.html"
    model = CropSeason
    fields = crop_season_fields

    def get_queryset(self):
        return crop_seasons_filter(self.request.user)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CropSeasonListView, self).dispatch(*args, **kwargs)


class CropSeasonEventsInline(InlineFormSet):
    model = CropSeasonEvent
    can_delete=False
    fields = [
               'field',
               'crop_event',
               'date',
             ]
    extra = 0

    def get_factory_kwargs(self):
        kwargs = super(CropSeasonEventsInline, self).get_factory_kwargs()
        kwargs[ 'extra' ] = self.extra
        return kwargs


class CropSeasonEventsInlineReadonly(ReadonlyFormset, CropSeasonEventsInline):
    class NewMeta:
        readonly = [ 'crop_event', ]# 'field' ]
        hidden = [ 'field' ]


class CropSeasonUpdateView(UpdateWithInlinesView):
    model = CropSeason
    fields = crop_season_fields
    inlines = [ CropSeasonEventsInlineReadonly ]
    template_name = 'farms/crop_season_and_crop_season_events.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """
        This function ensures that the user has the right to access
        this object by comparing the primary key of this object to the
        list of primary keys constructed from a query of objects where
        this user is either the farmer or the one of the users.
        """
        self.crop_season_list = crop_seasons_filter(self.request.user)
        user_pk = int(kwargs['pk'])
        pk_list = map( lambda x: int(x.pk), self.crop_season_list )
        if not user_pk in pk_list:
            return redirect( reverse('crop_season_list') )
        else:
            return super(CropSeasonUpdateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('crop_season_id', args=[self.object.pk])

    def get_queryset(self):
        user = self.request.user
        queryset = super(CropSeasonUpdateView, self).get_queryset()

        queryset = queryset.filter( Q(field_list__farm__farmer=user) |
                                    Q(field_list__farm__users=user)
                                  )

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super(CropSeasonUpdateView, self).get_context_data(**kwargs)
        field_list = context['object'].field_list.all()
        context['field_list'] = field_list
        return context

    def get_form(self, *args, **kwargs):
        """
        Ensure that the "Field List" widget only shows fields that correspind to this user
        """
        form = super(CropSeasonUpdateView, self).get_form(*args, **kwargs)
        form.fields["field_list"].queryset = fields_filter(self.request.user)
        return form



class CropSeasonCreateView(CreateWithInlinesView):
    model = CropSeason
    fields = crop_season_fields
    inlines = [ CropSeasonEventsInline ]
    template_name = 'farms/crop_season_and_crop_season_events.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CropSeasonCreateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('crop_season_id', args=[self.object.pk])

    def get_queryset(self):
        user = self.request.user
        queryset = super(CropSeasonCreateView, self).get_queryset()

        queryset = queryset.filter( Q(field_list__farm__farmer=user) |
                                    Q(field_list__farm__users=user)
                                  )

        return queryset.distinct()

    def get_factory_kwargs(self):
        kwargs = super(CropSeasonEventsInline, self).get_factory_kwargs()
        #kwargs[ 'widgets' ] = self.widgets
        return kwargs

    def get_form(self, *args, **kwargs):
        form = super(CropSeasonCreateView, self).get_form(*args, **kwargs)
        form.fields["field_list"].queryset = fields_filter(self.request.user)
        return form



class CropSeasonDeleteView(DeleteView):
    template_name = "farms/crop_season_delete.html"
    model = CropSeason
    pk_field = 'pk'

    success_url = reverse_lazy('crop_season_list')

    crop_season_list = None

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """
        This function ensures that the user has the right to access
        this object by comparing the primary key of this object to the
        list of primary keys constructed from a query of objects where
        this user is either the farmer or the one of the users.
        """
        self.crop_season_list = crop_seasons_filter(self.request.user)
        user_pk = int(kwargs['pk'])
        pk_list = map( lambda x: int(x.pk), self.crop_season_list )
        if not user_pk in pk_list:
            return redirect( reverse('crop_season_list') )
        else:
            return super(CropSeasonDeleteView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(CropSeasonDeleteView, self).get_context_data(*args, **kwargs)
        context['crop_season_list'] = self.crop_season_list
        return context
