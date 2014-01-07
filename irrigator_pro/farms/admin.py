from django.contrib import admin
from farms.models import *
from common.models import Audit, Comment, Location, NameDesc
from common.admin import AuditAdmin

############
### Farm ###
############
class FarmAdmin(AuditAdmin):
    fields = [ 'farmer' ] + NameDesc.fields + [ 'users' ] + Location.fields + Comment.fields 
    list_display  = [ 'farmer', 'get_users' ] + Location.fields
    list_editable = list_display[2:]
    save_on_top = True

admin.site.register(Farm, FarmAdmin)

#############
### Field ###
#############
class FieldAdmin(AuditAdmin):
    fields = [ 'farm', 'acres', 'soil_type', 'irr_capacity', 'comment' ] #+ Comment.fields 
    list_display  = fields
    list_editable = fields[1:]
    save_on_top = True

admin.site.register(Field, FieldAdmin)

#################
### Soil Type ###
#################
class SoilTypeAdmin(AuditAdmin):
    fields = NameDesc.fields + Comment.fields
    list_display  = ['id'] + NameDesc.fields + Comment.fields
    list_editable = fields[1:]
    save_on_top = True

admin.site.register(SoilType, SoilTypeAdmin)

#################
### Soil Type ###
#################
class SoilTypeParametersAdmin(AuditAdmin):
    fields = [ 'soil_type', 'depth', 'intercept', 'slope' ] + Comment.fields
    list_display  = fields[0:4]
    list_editable = fields[1:4]
    save_on_top = True

admin.site.register(SoilTypeParameters, SoilTypeParametersAdmin)




admin.site.register(Crop)
admin.site.register(CropEvent)
admin.site.register(Planting)
admin.site.register(PlantingEvents)
admin.site.register(WaterHistory)
admin.site.register(Probes)
admin.site.register(ProbeReadings)
admin.site.register(RawProbeReadings)

