from django.db import models
from django.contrib.auth.models import User
from common.models import Audit, Comment, Location, NameDesc



class SMS_Info(Audit):
    STATUS_CHOICES = ['New', 'Submitted', 'Validated', 'Denied']
    number      = models.CharField(max_length=20, blank=True, unique = True)
    status      = models.CharField(max_length=20, blank=True, default = STATUS_CHOICES[0])

    def  __unicode__(self):
        return self.number



class Contact_Info(Location, Audit):
    # from Location: address_1, address_2, city, state, zipcode, country
    # from Audit: cdate, cuser, mdate, muser
    
    # user
    user      = models.OneToOneField(User, related_name="contact_info_user")
    
    # contact information
    phone     = models.CharField(max_length=20, blank=True)
    #mobile    = models.CharField(max_length=20, blank=True)
    sms_info  = models.ForeignKey(SMS_Info, blank=True, null=True)
    fax       = models.CharField(max_length=20, blank=True)
    
    def user_first_name(self):
        return self.user.first_name
    
    def user_last_name(self):
        return self.user.last_name

    def user_full_name(self):
        return self.user.first_name + ' ' + self.user.last_name

    def __unicode__(self):
        return self.user.email + ": " + self.get_address()
    
    class Meta: 
        verbose_name        = 'Contact Information' 
        verbose_name_plural = 'Contact Information'




