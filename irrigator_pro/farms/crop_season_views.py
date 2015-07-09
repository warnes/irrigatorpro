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
                   'season_end_date',
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
    fields = [ 'field',
               'crop_event',
               'date',
             ]
    extra = 0

    def get_factory_kwargs(self):
        kwargs = super(CropSeasonEventsInline, self).get_factory_kwargs()
        kwargs[ 'extra' ] = self.extra
        return kwargs

    def add_fields(self, form, index):
        super(CropSeasonEventsInline, self).add_fields(form, index)
        Form.fields["event_order"]       = forms.CharField()
        form.fields["event_duration"]    = forms.CharField()
        form.fields["event_description"] = forms.TextField()
        form.fields["key_event"]         = forms.BooleanField()

    def construct_formset(self, *args, **kwargs):
        formset = super(CropSeasonEventsInline, self).construct_formset(*args, **kwargs)
        for form in formset:
            form.instance.event_order       = form.instance.get_event_order()
            form.instance.event_duration    = form.instance.get_event_duration()
            form.instance.event_description = form.instance.get_event_description()
            form.instance.key_event         = form.instance.get_key_event()
        return formset


class CropSeasonEventsInlineReadonly(ReadonlyFormset, CropSeasonEventsInline):

    class NewMeta:
        readonly = [ 'crop_event', ]
        hidden = [ 'field', ]


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
            retval = super(CropSeasonUpdateView, self).dispatch(*args, **kwargs)

        return retval

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

    def forms_valid(self, form, inlines):
        # If the type of crop has changed, the CropEvent in the
        # formset will contain invalid inforamtiom so ignore it.
        if 'crop' in form.changed_data:
            retval = super(CropSeasonUpdateView, self).forms_valid(form, [] )
        else:
            retval = super(CropSeasonUpdateView, self).forms_valid(form, inlines)

        self.object.save()
        return retval


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

    def forms_valid(self, form, inlines):
        retval = super(CropSeasonCreateView, self).forms_valid(form, inlines)
        self.object.save()
        self.object.delete_orphan_events(all=False)
        return retval


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
