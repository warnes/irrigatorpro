from django.db import models
from django.utils import timezone
from common.models import Audit, Comment, Location, NameDesc
from django.contrib.auth.models import User
from datetime import timedelta

import sys

############
### Farm ###
############

class Farm(NameDesc, Location, Comment, Audit):
    # from NameDesc: name, description
    # from Location: address_1, address_2, city, state, zipcode, country
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    farmer      = models.ForeignKey(User, related_name="farmers")
    users       = models.ManyToManyField(User)

    def get_users(self):
        user_list = self.users.all()
        if user_list:
            return ', '.join([ obj.username for obj in user_list])
        else:
            return ''

    def __unicode__(self):
        return u"Farmer %s - %s Farm" % ( self.farmer.username, self.name )

    class Meta:
        ordering = ["farmer"]
        pass


#############
### Field ###
#############

class Field(NameDesc, Comment, Audit):
    # from NameDesc:  name, description
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser

    farm          = models.ForeignKey(Farm)
    acres         = models.DecimalField(max_digits=5, decimal_places=2) # ###.##
    soil_type     = models.ForeignKey('SoilType')
    irr_capacity  = models.DecimalField(max_digits=3, decimal_places=2) # #.##

    def __unicode__(self):
        return u"Farm %s - Field %s" % ( self.farm.name, self.name )

    class Meta:
        ordering = ["farm__farmer__username", "farm__name", "name"]


#################
### Soil Type ###
#################

class SoilType(NameDesc, Comment, Audit):
    # from NameDesc:  name, description
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    max_available_water = models.DecimalField(max_digits=3,
                                                      decimal_places=2,
                                                      blank=True,
                                                      null=True) # #.##

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Soil Type"



class SoilTypeParameter(Comment, Audit):
    DEPTH_VALUES = ( 8, 16, 24 )
    DEPTH_CHOICES = ( (8,  "8 inches"),
                      (16, "16 inches"),
                      (24, "24 inches") )

    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    soil_type           = models.ForeignKey(SoilType)
    depth               = models.PositiveSmallIntegerField(choices=DEPTH_CHOICES)
    intercept           = models.FloatField("Intercept Term (B0)")
    slope               = models.FloatField("Slope Term (B1)")

    def __unicode__(self):
        return u"%s - %s inches" % (self.soil_type, self.depth)

    class Meta:
        ordering = ["soil_type__name", "depth"]
        verbose_name = "Soil Type Parameters"


############
### Crop ###
############

class Crop(NameDesc, Comment, Audit):
    # from NameDesc:  name, description
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    variety = models.CharField(max_length=32,
                               blank=True,
    )

    def __unicode__(self):
        return u"%s - %s" % (self.name, self.variety)

    class Meta:
        ordering = ['name']


class CropEvent(NameDesc, Comment, Audit):
    # from NameDesc:  name, description
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    crop                    = models.ForeignKey(Crop)
    days_after_emergence    = models.PositiveSmallIntegerField()
    daily_water_use         = models.DecimalField(max_digits=3, decimal_places=2)

    def __unicode__(self):
        return u"%s: %s" % (self.crop, self.name)

    class Meta:
        ordering = [ 'crop__name', 'days_after_emergence' ]
        verbose_name = "Crop Event"

    todo = """
           Add code to ensure that event_order is unique and sequential.
           """

########################################
### Planting (Crop + Season + Fields) ##
########################################


class Planting(NameDesc, Comment, Audit):
    # from NameDesc:  name, description
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    farm              = models.ForeignKey(Farm)
    fields            = models.ManyToManyField(Field)
    crop              = models.ForeignKey(Crop)
    planting_date     = models.DateField() ## May need a better name

    def get_fields(self):
        field_list = self.fields.all()
        if field_list:
            return ', '.join([ obj.fieldname for obj in field_list])
        else:
            return ''

    def __unicode__(self):
        return u"%s: %s - %s" % (self.farm, self.planting_date, self.crop)

    # Create a full set of PlantingEvents when a new Planting is saved
    def save(self, *args, **kwargs):
        super(Planting, self).save(*args, **kwargs) # Call the "real" save() method.

        crop_events = CropEvent.objects.filter(crop = self.crop).order_by("days_after_emergence")
        planting_events = PlantingEvent.objects.filter(planting=self)

        print "Here!!"

        for ce in crop_events:
            print "Checking whether Planting %s has CropEvent %s" % ( self, ce )
            matches = filter( lambda pe: pe.crop_event==ce, planting_events)
            if not matches:
                print "Adding CropEvent %s to Planting %s" % ( ce, self )
                pe = PlantingEvent(planting=self,
                                   crop_event=ce,
                                   date = self.planting_date + timedelta(days=ce.days_after_emergence),
                                   cdate = timezone.now(),
                                   cuser = self.muser,
                                   mdate = timezone.now(),
                                   muser = self.muser
                               )
                pe.save()

    class Meta:
        ordering = [ 'farm', 'planting_date', 'crop' ]


class PlantingEvent(Comment, Audit):
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    planting    = models.ForeignKey(Planting)
    crop_event  = models.ForeignKey(CropEvent)
    date        = models.DateField(default=timezone.now())

    def get_days_after_emergence(self):
        #if self.planting:
        return self.crop_event.days_after_emergence

    def get_planting_date(self):
        #if self.planting:
        return self.planting.planting_date

    def get_default_date(self):
        return self.get_planting_date() + timedelta(days=self.get_days_after_emergence())

    class Meta:
        verbose_name = "Planting Event"

    def __unicode__(self):
        return u"Planting Event: %s - %s: %s" % (self.planting, self.crop_event.name, self.date)



#############
### Water ###
#############

class WaterHistory(Comment, Audit):
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    farm                    = models.ForeignKey(Farm)
    field                   = models.ManyToManyField(Field)
    date                    = models.DateField()
    rain                    = models.DecimalField("rainfall in inches",
                                                  max_digits=4, decimal_places=2, default=0.0) # ##.##
    irrigation              = models.DecimalField("irrigation in inches",
                                                  max_digits=4, decimal_places=2, default=0.0) # ##.##
    available_water_content = models.DecimalField(max_digits=4, decimal_places=2, default=0.0, # ##.##
                                                  blank=True, null=True)   # Null --> Not yet calculated

    def get_fields(self):
        field_list = self.field.all()
        if field_list:
            return ', '.join([ obj.name for obj in field_list])
        else:
            return ''

    class Meta:
        verbose_name        = "Water History"
        verbose_name_plural = "Water Histories"

    def __unicode__(self):
        return u"Water History Entry for %s %s" % (field, date)


#############################
### Probe & Measurements ###
#############################

class Probe(NameDesc, Comment, Audit):
    # from NameDesc:  name, description
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    farm        = models.ForeignKey(Farm)
    field       = models.ManyToManyField(Field, limit_choices_to={'farm':farm} )
    farm_code   = models.CharField(max_length=10)
    probe_code  = models.CharField(max_length=10)
    unique_together = ( ("farm_code", "node_id",), )

    def __unicode__(self):
        return u"Probe for '%s' with farm code '%s' probe code '%s' " % (field, farm_code, probe_code)


class ProbeReading(Audit):
    """
    Model for CSV data read from probe files
    """

    # from Audit: cdate, cuser, mdate, muser

    ## From filename
    farm_code           = models.CharField(max_length=10)
    file_date           = models.DateField()

    ## From file contents
    reading_date        = models.DateTimeField()
    probe_code          = models.CharField(max_length=10)
    radio_id            = models.CharField(max_length=10)
    battery_voltage     = models.DecimalField(max_digits=3, decimal_places=2) #   #.##
    battery_percent     = models.DecimalField(max_digits=5, decimal_places=2) # ###.##
    soil_potential_8    = models.DecimalField(max_digits=5, decimal_places=2) # ###.##
    soil_potential_16   = models.DecimalField(max_digits=5, decimal_places=2) # ###.##
    soil_potential_32   = models.DecimalField(max_digits=5, decimal_places=2) # ###.##
    circuit_board_temp  = models.DecimalField(max_digits=5, decimal_places=2) # ###.##
    thermocouple_1_temp = models.DecimalField(max_digits=5, decimal_places=2) # ###.##
    thermocouple_2_temp = models.DecimalField(max_digits=5, decimal_places=2) # ###.##
    minutes_awake       = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = "Raw Probe Reading"
        unique_together = ( ("farm_code", "probe_code", "reading_date",), )

    def __unicode__(self):
        return u"ProbeReading %s-%s" % ( farm_code.strip(), probe_code.strip() )

    def _dedupe(self):

        lastSeenVals = (None, None, None)
        rows = ProbeReading.objects.all().order_by( "farm_code", "probe_code", "reading_date", )

        for row in rows:
            if (row.farm_code, row.probe_code, row.reading_date ) == lastSeenVals:
                row.delete() # We've seen this id in a previous row
                print ".",
                sys.stdout.flush()
            else: # New id found, save it and check future rows for duplicates.
               lastSeenVals = ( row.farm_code, row.probe_code, row.reading_date )


class ProbeSync(Audit):
    """
    Model for tracking automatic import of probe information from ftp site
    """
    datetime  = models.DateTimeField()
    success   = models.BooleanField(default=False)
    message   = models.TextField()
    nfiles    = models.PositiveIntegerField(default=0)
    nrecords  = models.PositiveIntegerField(default=0)
    filenames = models.TextField(blank=True)

    class Meta:
        get_latest_by = "datetime"

    def __unicode__(self):
        return u"ProbeSync %s" % self.datetime
