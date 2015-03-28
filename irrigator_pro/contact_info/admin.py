from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from contact_info.models import Contact_Info
from common.admin  import AuditAdmin

class Contact_Info_Inline(admin.StackedInline):
    model = Contact_Info
    fk_name = 'user'
    can_delete = False
    readonly_fields = ( 'cdate',
                        'mdate',
                        'cuser',
                        'muser',
                      )


class UserAdmin(UserAdmin):
    inlines = ( Contact_Info_Inline, )
    list_display  = ( 'pk', 'username', 'email', 'first_name', 'last_name' )
    list_editable = list_display[1:]
    save_on_top = True

    ## Set cuser and muser for the Contact_Info inline
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            if isinstance(instance, Contact_Info):
                # only set cname on create
                if not change:
                    instance.cuser = request.user

                # always set mname 
                instance.muser = request.user
                
            instance.save()


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

class Contact_Info_Admin(AuditAdmin):
    fields = (
        'user',
        'address_1',
        'address_2',
        'city',
        'county',
        'state',
        'zipcode',
        'phone',
#        'mobile',
        'fax',
        'cdate',
        'mdate',
        'cuser',
        'muser',        
    )
    list_display  = fields
    list_editable = fields[1:-4]
    save_on_top = True

admin.site.register(Contact_Info, Contact_Info_Admin)
