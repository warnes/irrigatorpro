from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from contact_info.models import Contact_Info

class AuditAdmin(admin.ModelAdmin):
    readonly_fields = ( 'cdate',
                        'mdate',
                        'cuser',
                        'muser',
                      )
    save_on_top = True

    def save_model(self, request, obj, form, change):
        # only set cname on create
        if not change:
            obj.cuser = request.user

        # always set mname
        obj.muser = request.user

        obj.save()


def save_audit_model(self, request, obj, form, change):
    # only set cname on create
    if not change:
        obj.cuser = request.user

        # always set mname
        obj.muser = request.user

        obj.save()


