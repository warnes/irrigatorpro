from django.db import models
from django.contrib.auth.models import User

class User_Info(models.Model):
    user      = models.OneToOneField(User)
    address_1 = models.CharField(max_length=50, verbose_name="address line 1")
    address_2 = models.CharField(max_length=50, verbose_name="address line 2", blank=True)
    city      = models.CharField(max_length=32)
    state     = models.CharField(max_length=32)
    zipcode   = models.CharField(max_length=10, verbose_name="zip/postal code")
    country   = models.CharField(max_length=32, blank=True)
    phone     = models.CharField(max_length=20, blank=True)
    mobile    = models.CharField(max_length=20, blank=True)
    fax       = models.CharField(max_length=20, blank=True)
    join_date = models.DateField(auto_now_add=True, verbose_name="member since")

    def name(self):
        "" + first + " " + last

    def address(self):
        " %s, %s, %s, %s %s, %s" % (self.address_1, self.address_2, self.city, self.state, self.zipcode, self.country )

    def address_label(self):
        """
        %s
        %s
        %s, %s %s
        %s
        """ % (self.address_1, self.address_2, self.city, self.state, self.zipcode, self.country )

    def __unicode__(self):
        return self.user.name()




