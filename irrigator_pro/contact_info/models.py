from django.db import models
from django.contrib.auth.models import User
from common.models import Audit, Comment, Location, NameDesc
from django.core.exceptions import ObjectDoesNotExist

from farms.models import Farm, InvitedUser


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


    ###
    ## Override the save method to process the fact that this user can be an invited user
    ## assigned to some farms. In that case remove the relevant invited_user record, add this
    ## new user to all the farms.
    ##
    ## This creates a bidirectional relationship between the contact_info and farm projects.
    ## Do we want to break it?

    def save(self, *args, **kwargs):
        self.check_invited_user()
        super(Contact_Info, self).save(*args, **kwargs) # Call the "real" save() method.


    def check_invited_user(self):
        try:
            invited = InvitedUser.objects.get(email = self.user.email)
            for f in invited.farms.all():
                f.users.add(self.user)
                f.save()
            invited.delete()

        except ObjectDoesNotExist:
            # Was not an invited user. Nothing to do
            pass

    
    class Meta: 
        verbose_name        = 'Contact Information' 
        verbose_name_plural = 'Contact Information'




