from django.db import models
from django.contrib.auth.models import User

class NameDesc(models.Model):
    # name and description
    name        = models.CharField(max_length=32)
    description = models.TextField(blank=True)

    fields = ['name', 'description']

    class Meta:
        abstract = True

class Location(models.Model):
    address_1 = models.CharField(max_length=50, verbose_name="address line 1")
    address_2 = models.CharField(max_length=50, verbose_name="address line 2", blank=True)
    city      = models.CharField(max_length=32)
    county    = models.CharField(max_length=32)
    state     = models.CharField(max_length=2)
    zipcode   = models.CharField(max_length=10, verbose_name="zip/postal code")
    country   = models.CharField(max_length=32, blank=True, default='United States')

    fields = ['address_1', 'address_2', 'city', 'county', 'state', 'zipcode']

    class Meta:
        abstract = True

    def get_address(self):
        return " %s, %s, %s, %s %s, %s" % ( self.address_1, self.address_2, self.city, self.state, self.zipcode, self.country )

    def get_address_label(self):
        """
        %s
        %s
        %s, %s %s
        %s
        return """ % (self.address_1, self.address_2, self.city, self.state, self.zipcode, self.country )

class Audit(models.Model):

    cdate     = models.DateTimeField(auto_now_add=True, 
                                     verbose_name="creation date",
                                     #editable=False,
                                     )
    cuser     = models.ForeignKey(User,
                                  related_name="%(app_label)s_%(class)s_cusers",
                                  verbose_name="creator",
                                  #editable=False
                                  )

    mdate     = models.DateTimeField(auto_now=True, 
                                     verbose_name="last modification date",
                                     #editable=False
                                     )
    muser     = models.ForeignKey(User,
                                  related_name="%(app_label)s_%(class)s_musers",
                                  verbose_name="last modifcation user",
                                  #editable=False
                                  )

    fields = [ 'cdate', 'cuser', 'mdate', 'muser' ]

    def get_creation_info(self):
        return "Changed by %s on %s" % ( cuser, cdate )

    def get_modification_info(self):
        return "Modified by %s on %s" % ( muser, mdate )

    class Meta:
        abstract = True

class Comment(models.Model):
    comment = models.TextField(blank=True)

    fields = [ 'comment', ]

    class Meta:
        abstract = True
