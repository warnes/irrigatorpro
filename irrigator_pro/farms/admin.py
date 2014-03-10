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

    list_display  = [ 'farmer', 'name', 'get_users' ] + Location.fields
    list_editable = ['name'] + list_display[3:]
    list_filter = ['farmer']


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
    list_filter = ['farm__farmer', 'farm']

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
    list_filter   = ['soil_type', ]


admin.site.register(SoilTypeParameter, SoilTypeParameterAdmin)

############
### Crop ###
############
class CropEventInline(admin.TabularInline):
    model = CropEvent
    fields = [ 'crop', 'order', ] \
             + NameDesc.fields \
             + [
                 'duration',
                 'daily_water_use',
                 'key_event',
                ] \
             + Comment.fields


class CropAdmin(AuditAdmin):
    fields = [ 'name', 'variety', 'description', 'max_root_depth',
               'season_length_days' ] \
             + Comment.fields \
             + Audit.fields
    list_display  = ['id', 'name', 'variety', 'description',
                     'max_root_depth', 'season_length_days' ]
    list_editable = list_display[1:]
    inlines = [ CropEventInline ]
    list_filter = ['name']

#readonly = False
readonly = True
if not readonly:
    admin.site.register(Crop, CropAdmin)

###################
### Crop Events ###
###################

class CropEventAdmin(AuditAdmin):
    fields = [ 'crop', 'order', ] \
             + NameDesc.fields \
             + [
                 'duration',
                 'daily_water_use',
                 'key_event',
                ] \
             + Comment.fields \
             + Audit.fields
    list_display  = [ 'crop',
                      'order',
                      'name',
                      'duration',
                      'daily_water_use',
                      'key_event',
                    ]
    list_editable = list_display[1:]
    list_filter = ['crop', 'key_event', ]

admin.site.register(CropEvent, CropEventAdmin)

################
### CropSeason ###
################

class CropSeasonEventInline(admin.TabularInline):
    model = CropSeasonEvent
    fields = [ 'field', 'crop_event', 'date', 'get_default_date' ] \
             + Comment.fields
    readonly_fields = [ 'get_default_date' ]
    extra=0


class CropSeasonAdmin(AuditAdmin):
    fields = NameDesc.fields \
             + [ 'field_list',
                 'season_start_date',
                 'season_end_date',
                 'crop',
                ] \
             + Comment.fields \
             + Audit.fields
    list_display  = ['pk', 'name', 'description', 'get_field_list', ] + fields[4:-5]
    list_editable = [ 'name', 'description', ] + fields[4:-5]
    inlines = [ CropSeasonEventInline ]
    list_filter = ['field_list__farm__farmer',
                   'field_list__farm',
                   'season_start_date']

    # def get_form(self, request, obj=None, **kwargs):
    #     kwargs['formfield_callback'] = partial(self.formfield_for_dbfield, request=request, obj=obj)
    #     return super(CropSeasonAdmin, self).get_form(request, obj, **kwargs)

admin.site.register(CropSeason, CropSeasonAdmin)

######################
### CropSeason Event ###
######################

class CropSeasonEventAdmin(AuditAdmin):
    fields = [ 'field', 'crop_season', 'crop_event', 'date' ] \
             + Comment.fields
    list_display  = fields[:-1]
    list_editable = [ 'date' ]
    list_filter = ['crop_season',
                   'crop_season__field_list__farm__farmer',
                   'crop_season__field_list__farm',
                   'crop_season__season_start_date']

admin.site.register(CropSeasonEvent, CropSeasonEventAdmin)

#####################
### Water History ###
#####################

class WaterHistoryAdmin(AuditAdmin):
    fields = [ 'field_list', 'date', 'rain', 'irrigation', 'available_water_content' ] \
             + Comment.fields
    list_display  = [ 'pk', 'get_field_list' ] + fields[2:-1]
    list_editable = [ 'rain', 'irrigation' ]
    readonly_fields = [ 'available_water_content' ]
    list_filter = [ 'field_list__farm__farmer', 'field_list__farm', 'date' ]

    # def get_form(self, request, obj=None, **kwargs):
    #     kwargs['formfield_callback'] = partial(self.formfield_for_dbfield, request=request, obj=obj)
    #     return super(WaterHistoryAdmin, self).get_form(request, obj, **kwargs)

admin.site.register(WaterHistory, WaterHistoryAdmin)


#############
### Probe ###
#############

class ProbeAdmin(AuditAdmin):
    fields = NameDesc.fields \
             + [ 'field_list', 'radio_id' ] \
             + Comment.fields \
             + Audit.fields
    list_display  = [ 'pk',
                      'radio_id',
                      'name',
                      'get_field_list',
                    ]
    list_editable = [ 'radio_id', 'name' ]
    list_filter = [ 'field_list__farm__farmer',
                    'field_list__farm',
                  ]

    # def get_form(self, request, obj=None, **kwargs):
    #     kwargs['formfield_callback'] = partial(self.formfield_for_dbfield, request=request, obj=obj)
    #     return super(ProbeAdmin, self).get_form, obj, **kwargs)


admin.site.register(Probe, ProbeAdmin)


#################
### ProbeSync ###
#################

class ProbeSyncAdmin(AuditAdmin):
    fields = [ 'datetime', 'success', 'message', 'nfiles', 'nrecords', 'filenames' ] \
             + Audit.fields
    list_display  = [ 'datetime', 'success', 'message', 'nfiles', 'nrecords' ]
    list_editable = []
    list_filter = [ 'datetime', 'success' ]

admin.site.register(ProbeSync, ProbeSyncAdmin)


####################
### ProbeReading ###
####################

class ProbeReadingAdmin(AuditAdmin):
    fields = [ 'farm_code',
               'probe_code',
               'file_date',
               'reading_datetime',
               'radio_id',
               'soil_potential_8',
               'soil_potential_16',
               'soil_potential_24',
               'battery_voltage',
               'battery_percent',
               'circuit_board_temp',
               'thermocouple_1_temp',
               'thermocouple_2_temp',
               'minutes_awake',
               'source'
             ]
    list_display = [ 'radio_id',
                     'reading_datetime',
                     'soil_potential_8',
                     'soil_potential_16',
                     'soil_potential_24',
                     'battery_voltage',
                     'battery_percent',
                     'source',
                   ]
    list_editable = []
    list_filter = [ 'farm_code', 'radio_id', 'reading_datetime', 'reading_datetime', 'source' ]


admin.site.register(ProbeReading, ProbeReadingAdmin)
