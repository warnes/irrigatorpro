from django.db import models
from django.utils import timezone
from common.models import Audit, Comment, Location, NameDesc
from django.contrib.auth.models import User

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
            return ', '.join([ obj.userid for obj in user_list])
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
    acres         = models.DecimalField(max_digits=4, decimal_places=2) # ###.##
    soil_type     = models.ForeignKey('SoilType')
    irr_capacity  = models.PositiveSmallIntegerField()

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
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class SoilTypeParameters(Comment, Audit):
    DEPTH_VALUES = ( 8, 16, 24 )
    DEPTH_CHOICES = ( (8,  "8 inches"),
                      (16, "16 inches"),
                      (24, "24 inches") )

    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    soil_type    = models.ForeignKey(SoilType)
    depth        = models.PositiveSmallIntegerField(choices=DEPTH_CHOICES)
    intercept    = models.FloatField("Intercept Term (B0)")
    slope        = models.FloatField("Slope Term (B1)")

    def __unicode__(self):
        return u"%s - %s inches" % (self.soil_type, self.depth)

    class Meta:
        ordering = ["soil_type__name", "depth"]



############
### Crop ###
############

class Crop(NameDesc, Comment, Audit):
    # from NameDesc:  name, description
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    variety     = models.CharField(max_length=32, blank=True)

    class Meta:
        ordering = ['name']


class CropEvent(NameDesc, Comment, Audit):
    # from NameDesc:  name, description
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    crop                    = models.ForeignKey(Crop)
    prior_event             = models.ForeignKey('CropEvent')
    event_order             = models.PositiveSmallIntegerField()
    days_after_prior_early  = models.PositiveSmallIntegerField()
    days_after_prior_normal = models.PositiveSmallIntegerField()    
    days_after_prior_late   = models.PositiveSmallIntegerField()    

    class Meta:
        ordering = [ 'crop__name', 'event_order' ]

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
    fields            = models.ManyToManyField(Field)
    crop              = models.ForeignKey(Crop)
    date              = models.DateField() ## May need a better name


class PlantingEvents(Comment, Audit):
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    planting          = models.ForeignKey(Planting)
    event             = models.ForeignKey(CropEvent)
    event_date        = models.DateField()


#############
### Water ###
#############

class WaterHistory(Comment, Audit):
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    farm        = models.ForeignKey(Farm)
    field       = models.ManyToManyField(Field, limit_choices_to={'farm':farm} )
    date        = models.DateField()
    rain        = models.DecimalField("rainfall in inches", max_digits=4, decimal_places=2, default=0.0)   # ##.##
    irrigation  = models.DecimalField("irrigation in inches", max_digits=4, decimal_places=2, default=0.0) # ##.##
    

#############################
### Probe & Measurements ###
#############################

class Probe(NameDesc, Comment, Audit):
    # from NameDesc:  name, description
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    farm        = models.ForeignKey(Farm)
    field       = models.ManyToManyField(Field, limit_choices_to={'farm':farm} )
    probe_id    = models.CharField(max_length=10)


class ProbeReadings(Audit):
    # from Audit: cdate, cuser, mdate, muser
    probe               = models.ForeignKey(Probe)
    date_time           = models.DateTimeField()
    soil_potential_8    = models.DecimalField(max_digits=4, decimal_places=2) # ##.##
    soil_potential_16   = models.DecimalField(max_digits=4, decimal_places=2) # ##.##
    soil_potential_32   = models.DecimalField(max_digits=4, decimal_places=2) # ##.##
    

class RawProbeReadings(Audit):
    """
    Model for CSV data read from probe files
    """

    # from Audit: cdate, cuser, mdate, muser

    ## From filename
    farm_code           = models.CharField(max_length=10)
    file_date           = models.DateTimeField()

    ## From file contents
    reading_date        = models.DateTimeField()
    node_id             = models.CharField(max_length=10)
    radio_id            = models.CharField(max_length=10)
    battery_voltage     = models.DecimalField(max_digits=3, decimal_places=2) #   #.##
    battery_percent     = models.DecimalField(max_digits=5, decimal_places=2) # ###.##
    soil_potential_8    = models.DecimalField(max_digits=4, decimal_places=2) #  ##.##
    soil_potential_16   = models.DecimalField(max_digits=4, decimal_places=2) #  ##.##
    soil_potential_32   = models.DecimalField(max_digits=4, decimal_places=2) #  ##.##
    circuit_board_temp  = models.DecimalField(max_digits=4, decimal_places=2) #  ##.##
    thermocouple_1_temp = models.DecimalField(max_digits=4, decimal_places=2) #  ##.##
    thermocouple_2_temp = models.DecimalField(max_digits=4, decimal_places=2) #  ##.##
    minutes_awake       = models.PositiveSmallIntegerField()
    



