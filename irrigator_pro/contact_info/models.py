from django.db import models
from emailuser.models import EmailUser as User
from common.models import Audit, Comment, Location, NameDesc

class Contact_Info(Location, Audit):
    # from Location: address_1, address_2, city, state, zipcode, country
    # from Audit: cdate, cuser, mdate, muser

    # user
    user      = models.OneToOneField(User, related_name="contact_info_user")

    # contact information
    phone     = models.CharField(max_length=20, blank=True)
    mobile    = models.CharField(max_length=20, blank=True)
    fax       = models.CharField(max_length=20, blank=True)

    def user_first_name(self):
        return self.user.first_name

    def user_last_name(self):
        return self.user.last_name


    def __unicode__(self):
        return self.user.email + ": " + self.get_address()

    class Meta: 
        verbose_name        = 'Contact Information' 
        verbose_name_plural = 'Contact Information' 

