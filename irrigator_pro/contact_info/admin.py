from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from contact_info.models import Contact_Info

class Contact_Info_Inline(admin.StackedInline):
    model = Contact_Info
    can_delete = False

class UserAdmin(UserAdmin):
    inlines = [ Contact_Info_Inline, ]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

class Contact_Info_Admin(admin.ModelAdmin):
    fields = [ 'user',
               'address_1',
               'address_2',
               'city',
               'state',
               'zipcode',
               'phone',
               'mobile',
               'fax',
             ]
    list_display = fields

admin.site.register(Contact_Info, Contact_Info_Admin)
