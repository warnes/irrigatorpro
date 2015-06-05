from extra_views import ModelFormSetView
from django.forms import Textarea, TextInput
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.forms.widgets import HiddenInput as HiddenInput

from farms.models import CropSeason, Field, Probe, WaterHistory

class Farms_FormsetView(ModelFormSetView):
    # model = WaterHistory
    # template_name = 'farms/water_history_list.html'
    # fields = [ 'date', 'field_list',  'rain', 'irrigation', 'comment' ]
    # widgets = {
    #    'comment':     Textarea(attrs={'rows':2, 'cols':20}),
    #    'description': Textarea(attrs={'rows':2, 'cols':20}),
    #    'date':        TextInput(attrs={'width':10, 'class':'hasDatePicker'}),
    #    }

    can_delete=True

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.season = kwargs.get('season', None)
        self.field  = kwargs.get('field', None)
        return super(Farms_FormsetView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        queryset = super(Farms_FormsetView, self).get_queryset()
        queryset = queryset.filter( Q(field_list__farm__farmer=user) |
                                    Q(field_list__farm__users=user) )
        if self.season:
            queryset = queryset.filter( crop_season=int(self.season) )
            if self.field:
                queryset = queryset.filter( field_list=int(self.field) )
        return queryset.distinct()

    def fields_filter(self, user, season=None, field=None):
        query = Field.objects.filter( Q(farm__farmer=user) |
                                     Q(farm__users=user) )
        if season:
            query = query.filter(cropseason=int(season))

        if field:
            query = query.filter(pk=int(field))

        return query.distinct()


    def crop_season_filter(self, user, season=None):
        query= CropSeason.objects.filter( Q(field_list__farm__farmer=user) |
                                          Q(field_list__farm__users=user) )
        if season:
            query = query.filter(pk=int(season))
        return query.distinct()

    def construct_formset(self, *args, **kwargs):
        formset = super(Farms_FormsetView, self).construct_formset(*args, **kwargs)
        for form in formset:
            if "field_list" in form.fields:
                form.fields["field_list"].queryset  = self.fields_filter(self.request.user,
                                                                         season=self.season,
                                                                         #field=self.field)
                                                                         )
            if "crop_season" in form.fields:
                form.fields["crop_season"].queryset = self.crop_season_filter(self.request.user,
                                                                              season=self.season)
        return formset


    def get_extra_form_kwargs(self):
        kwargs = super(Farms_FormsetView, self).get_extra_form_kwargs()
	if hasattr(self, 'season') and self.season is not None:
            kwargs['initial'] = { 'crop_season': int(self.season) }
        return kwargs


    def get_factory_kwargs(self):
        kwargs = super(Farms_FormsetView, self).get_factory_kwargs()
        if hasattr(self, 'widgets'):
            kwargs[ 'widgets' ] = self.widgets
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(Farms_FormsetView, self).get_context_data(**kwargs)
        if self.season:
            context['season'] = CropSeason.objects.get(pk=int(self.season))
        if self.field:
            context['field'] = Field.objects.get(pk=int(self.field))
        return context


class ProbeFormsetView(Farms_FormsetView):
    model = Probe
    template_name = 'farms/probe_list.html'
    fields = [ 'crop_season',
               'name',
               'description',
               'field_list',
               'radio_id',
               'comment']
    widgets = {
        'comment':     Textarea(attrs={'rows':2, 'cols':20}),
        'description': Textarea(attrs={'rows':2, 'cols':20}),
        'crop_season': HiddenInput(),
    }
    extra = 2
        
    ### formset_valid() is called when the formset is valid. In base class executed:
    ####    return HttpResponseRedirect(self.get_success_url())
    def formset_valid(self, formset):

        ### For each radio_id check that it does not conflict with another entry in the 
        ### database. The validation of the same radio_id in two different lines

        crop_season = CropSeason.objects.get(pk=self.season)
        ### on the same page is made by Django.
        for form in formset.forms:
            if len(form.cleaned_data)>0:
                rid = form.cleaned_data['radio_id']
                query = Probe.objects.filter(radio_id=rid).exclude(crop_season = crop_season).filter(Q(crop_season__season_end_date__gt = crop_season.season_start_date) &
                                                                                                     Q(crop_season__season_start_date__lt = crop_season.season_end_date))
                if len(query) > 0:
                    form.add_error('radio_id',"This radio is used for another overlapping crop season")
                    return self.formset_invalid(formset)
                
        return super(ProbeFormsetView, self).formset_valid(formset)


###    Just to document that it exists.
###    def formset_invalid(self, formset):
###        return super(ProbeFormsetView, self).formset_invalid(formset)





class WaterHistoryFormsetView(Farms_FormsetView):
    model = WaterHistory
    template_name = 'farms/water_history_list.html'
    fields = [ 'crop_season',
               'date',
               'field_list',
               'rain',
               'irrigation',
               'comment' ]
    widgets = {
        'comment':     Textarea(attrs={'rows':2, 'cols':20}),
        'description': Textarea(attrs={'rows':2, 'cols':20}),
        'date':        TextInput(attrs={'width':10, 'class':'hasDatePicker'}),
        'crop_season': HiddenInput(),
    }
    extra = 2
