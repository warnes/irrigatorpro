from django.contrib import admin

from .models import *

class UGAProbeDataAdmin(admin.ModelAdmin):
    list_filter = ['datetime', 'radio_id']
    pass

admin.site.register(UGAProbeData, UGAProbeDataAdmin)
