from django.contrib import admin
from farms.models import *
from common.models import Audit, Comment, Location, NameDesc
from common.admin import AuditAdmin

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
    save_on_top = True

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
    save_on_top = True
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
    save_on_top = True

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
            #if isinstance(instance, CropEventInline):

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
admin.site.register(Planting)
admin.site.register(PlantingEvent)
admin.site.register(WaterHistory)


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
    save_on_top = True


## to prevent editing until paid for!
admin.site.register(Probe, ProbeAdmin)

admin.site.register(ProbeReading)
admin.site.register(RawProbeReading)

