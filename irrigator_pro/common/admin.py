from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from emailuser.models import EmailUser as User
from contact_info.models import Contact_Info

class AuditAdmin(admin.ModelAdmin):
    readonly_fields = ( 'cdate',
                        'mdate',
                        'cuser',
                        'muser',
                      )
    save_on_top = True

    def save_model(self, request, obj, form, change):
        any_set = False
        for field in self.fields:
            if getattr(obj, field, None):
                any_set = True
                break

        if any_set:
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


