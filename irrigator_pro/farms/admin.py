from django.contrib import admin
from farms.models import *
from common.models import Audit, Comment, Location, NameDesc
from common.admin import AuditAdmin
from functools import partial

############
### Farm ###
############
class FarmAdmin(AuditAdmin):
    fields = [ 'farmer' ] \
             + NameDesc.fields \
             + [ 'users' ]  \
             + Location.fields \
             + Comment.fields \
             + Audit.fields

    list_display  = [ 'farmer', 'get_users' ] + Location.fields
    list_editable = list_display[2:]

admin.site.register(Farm, FarmAdmin)

#############
### Field ###
#############
class FieldAdmin(AuditAdmin):
    fields = [ 'farm', ] \
             + NameDesc.fields \
             + [ 'acres', 'soil_type', 'irr_capacity', ] \
             + Comment.fields \
             + Audit.fields

    list_display  = fields[:-4]
    list_editable = list_display[1:]

admin.site.register(Field, FieldAdmin)

#################
### Soil Type ###
#################
class SoilTypeParameterInline(admin.TabularInline):
    model = SoilTypeParameter
    fields = [ 'depth', 'intercept', 'slope' ]
    ordering = [ 'depth' ]


class SoilTypeAdmin(AuditAdmin):
    fields = NameDesc.fields \
             + [ "max_available_water" ] \
             + Comment.fields \
             + Audit.fields
    list_display  = [ 'id' ] \
                    + NameDesc.fields \
                    + [ "max_available_water" ] \
                    + Comment.fields
    list_editable = list_display[1:]
    inlines = [ SoilTypeParameterInline ]

    ## Set cuser and muser for the Contact_Info inline
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            # not sure why this doesn't work:
            #if isinstance(instance, CropEventInline):

            # only set cname on create
            if not hasattr(instance, 'cuser'):
                instance.cuser = request.user

            # always set mname
            instance.muser = request.user

            instance.save()




admin.site.register(SoilType, SoilTypeAdmin)

############################
### Soil Type Parameter ###
############################
class SoilTypeParameterAdmin(AuditAdmin):
    fields = [ 'soil_type', 'depth', 'intercept', 'slope' ] \
             + Comment.fields \
             + Audit.fields
    list_display  = [ 'id' ] + fields[0:4]
    list_editable = list_display[1:]

admin.site.register(SoilTypeParameter, SoilTypeParameterAdmin)

############
### Crop ###
############
class CropEventInline(admin.TabularInline):
    model = CropEvent
    fields = [ 'crop', ] \
             + NameDesc.fields \
             + [
                 'days_after_emergence',
                 'daily_water_use',
                ] \
             + Comment.fields


class CropAdmin(AuditAdmin):
    fields = [ 'name', 'variety', 'description' ] \
             + Comment.fields \
             + Audit.fields
    list_display  = ['id', 'name', 'variety', 'description']
    list_editable = list_display[1:]
    inlines = [ CropEventInline ]

    ## Set cuser and muser for the Contact_Info inline
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            # not sure why this doesn't work:

            # only set cname on create
            if not hasattr(instance, 'cuser'):
                instance.cuser = request.user

            # always set mname
            instance.muser = request.user

            instance.save()


readonly = True
if not readonly:
    admin.site.register(Crop, CropAdmin)


###################
### Crop Events ###
###################

class CropEventAdmin(AuditAdmin):
    fields = [ 'crop', ] \
             + NameDesc.fields \
             + [
                 'days_after_emergence',
                 'daily_water_use',
                ] \
             + Comment.fields \
             + Audit.fields
    list_display  = [ 'crop', 'name', 'days_after_emergence' ]
    list_editable = list_display[1:]

admin.site.register(CropEvent, CropEventAdmin)

################
### Planting ###
################

class PlantingEventInline(admin.TabularInline):
    model = PlantingEvent
    fields = [ 'crop_event', 'date', 'get_default_date' ] \
             + Comment.fields
    readonly_fields = [ 'get_default_date' ]
    extra=0


class PlantingAdmin(AuditAdmin):
    fields = [ 'farm', 'fields', ] \
             + NameDesc.fields \
             + [
                 'crop',
                 'planting_date'
                ] \
             + Comment.fields \
             + Audit.fields
    list_display  = fields[:-4]
    list_editable = list_display[1:]
    inlines = [ PlantingEventInline ]

    def get_form(self, request, obj=None, **kwargs):
        kwargs['formfield_callback'] = partial(self.formfield_for_dbfield, request=request, obj=obj)
        return super(PlantingAdmin, self).get_form(request, obj, **kwargs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        planting = kwargs.pop('obj', None)
        formfield = super(PlantingAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == "fields" and planting:
            formfield.queryset = Field.objects.filter(farm=planting.farm)
        return formfield

    ## Set cuser and muser for the Contact_Info inline
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            # not sure why this doesn't work:

            # only set cname on create
            if not hasattr(instance, 'cuser'):
                instance.cuser = request.user

            # always set mname
            instance.muser = request.user

            instance.save()

admin.site.register(Planting, PlantingAdmin)

######################
### Planting Event ###
######################

class PlantingEventAdmin(AuditAdmin):
    fields = [ 'planting', 'crop_event', 'date' ] \
             + Comment.fields
    list_display  = fields
    list_editable = list_display[1:]

admin.site.register(PlantingEvent, PlantingEventAdmin)

#####################
### Water History ###
#####################

class WaterHistoryAdmin(AuditAdmin):
    fields = [ 'farm', 'field', 'date', 'rain', 'irrigation', 'available_water_content' ] \
             + Comment.fields
    list_display  = [ 'farm', 'get_fields' ] + fields[2:]
    list_editable = [ 'rain', 'irrigation', 'comment' ]
    readonly_fields = [ 'available_water_content' ]

    def get_form(self, request, obj=None, **kwargs):
        kwargs['formfield_callback'] = partial(self.formfield_for_dbfield, request=request, obj=obj)
        return super(WaterHistoryAdmin, self).get_form(request, obj, **kwargs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        waterhistory = kwargs.pop('obj', None)
        formfield = super(WaterHistoryAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == "fields" and waterhistory:
            formfield.queryset = Field.objects.filter(farm=waterhistory.farm)
        return formfield


admin.site.register(WaterHistory, WaterHistoryAdmin)


#############
### Probe ###
#############

class ProbeAdmin(AuditAdmin):
    fields = [ 'farm', ] \
             + NameDesc.fields \
             + [ 'field', ] \
             + Comment.fields \
             + Audit.fields
    list_display  = NameDesc.fields[:-4]
    list_editable = list_display[1:]

## to prevent editing until paid for!
admin.site.register(Probe, ProbeAdmin)


####################
### Probe Events ###
####################

class ProbeReadingAdmin(AuditAdmin):
    fields = [ 'probe',
               'date_time',
               'soil_potential_8',
               'soil_potential_16',
               'soil_potential_32',
             ] \
             + Audit.fields
    list_display  = fields[:-4]
    list_editable = list_display[1:]

admin.site.register(ProbeReading, ProbeReadingAdmin)


#######################
### RawProbeReading ###
#######################

class RawProbeReadingAdmin(AuditAdmin):
    pass

admin.site.register(RawProbeReading, RawProbeReadingAdmin)

