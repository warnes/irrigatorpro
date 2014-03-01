from django.db import models
from django.utils import timezone
from common.models import Audit, Comment, Location, Location_Optional, NameDesc
from django.contrib.auth.models import User
from datetime import timedelta

import sys

############
### Farm ###
############

class Farm(NameDesc, Location_Optional, Comment, Audit):
    # from NameDesc: name, description
    # from Location: address_1, address_2, city, state, zipcode, country
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    farmer      = models.ForeignKey(User, related_name="farmers")
    users       = models.ManyToManyField(User, blank=True, verbose_name="Authorized Users")

    def get_farmer_and_user_list(self):
        retval = [self.farmer.pk] + map(lambda x: x.pk, self.users.all())
        print 'retval=', retval
        return retval

    def get_users(self):
        user_list = self.users.all()
        if user_list:
            return ', '.join([ obj.username for obj in user_list])
        else:
            return ''

    def __unicode__(self):
        return self.name

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
    acres         = models.DecimalField(max_digits=5, 
                                        decimal_places=2) # ###.##
    soil_type     = models.ForeignKey('SoilType')
    irr_capacity  = models.DecimalField(max_digits=3, 
                                        verbose_name='Irrigation Capacity',
                                        decimal_places=2) # #.##

    def __unicode__(self):
        return u"%s: %s" % (self.farm, self.name)

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
        #return u"%s - %s" % (self.name, self.variety)
        return self.name

    class Meta:
        ordering = ['name']


class CropEvent(NameDesc, Comment, Audit):
    # from NameDesc:  name, description
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    crop                    = models.ForeignKey(Crop)
    days_after_emergence    = models.PositiveSmallIntegerField()
    daily_water_use         = models.DecimalField(max_digits=3, 
                                                  decimal_places=2)

    def __unicode__(self):
        return u"%s: %s" % (self.crop, self.name)

    class Meta:
        ordering = [ 'crop__name', 'days_after_emergence' ]
        verbose_name = "Crop Event"

    todo = """
           Add code to ensure that event_order is unique and sequential.
           """

########################################
### CropSeason (Crop + Season + Fields) ##
########################################


class CropSeason(NameDesc, Comment, Audit):
    # from NameDesc:  name, description
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    season_start_date = models.DateField(default=timezone.now(),
                                         verbose_name="Season Start Date",
                                         ) ## May need a better name
    crop              = models.ForeignKey(Crop)
    field_list        = models.ManyToManyField(Field)

    def crop_season_year(self):
        return season_start_date.year
        
    def get_field_list(self):
        field_list = self.field_list.all()
        if field_list:
            return ', '.join([ obj.name for obj in field_list])
        else:
            return ''

    def __unicode__(self):
        return self.name

    # Create a full set of CropSeasonEvents when a new CropSeason is saved
    def save(self, *args, **kwargs):
        super(CropSeason, self).save(*args, **kwargs) # Call the "real" save() method.
        crop_events = CropEvent.objects.filter(crop = self.crop).order_by("days_after_emergence")
        crop_season_events = CropSeasonEvent.objects.filter(crop_season=self)
        for ce in crop_events:
            matches = filter( lambda pe: pe.crop_event==ce, crop_season_events)
            if not matches:
                pe = CropSeasonEvent(crop_season=self,
                                   crop_event=ce,
                                   date = self.season_start_date + timedelta(days=ce.days_after_emergence),
                                   cdate = timezone.now(),
                                   cuser = self.muser,
                                   mdate = timezone.now(),
                                   muser = self.muser
                               )
                pe.save()


    class Meta:
        ordering = [ 'season_start_date', 'crop' ]
        verbose_name = 'Crop Season'


class CropSeasonEvent(Comment, Audit):
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    crop_season = models.ForeignKey(CropSeason)
    crop_event  = models.ForeignKey(CropEvent)
    date        = models.DateField(default=timezone.now())

    def get_days_after_emergence(self):
        #if self.crop_season:
        return self.crop_event.days_after_emergence

    def get_crop_season_date(self):
        return self.crop_season.season_start_date

    def get_default_date(self):
        return self.get_season_start_date() + timedelta(days=self.get_days_after_emergence())

    class Meta:
        verbose_name = "CropSeason Event"

    def __unicode__(self):
        #return u"CropSeason Event: %s - %s: %s" % (self.crop_season, self.crop_event.name, self.date)
        return self.crop_event.name

    class Meta:
        unique_together = ( ("crop_season", "crop_event", ) , )
        ordering = [ 'crop_season__season_start_date', 'crop_event' ]



#############
### Water ###
#############

class WaterHistory(Comment, Audit):
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    field_list              = models.ManyToManyField(Field)
    date                    = models.DateField()
    rain                    = models.DecimalField("rainfall in inches",
                                                  max_digits=4, decimal_places=2, default=0.0) # ##.##
    irrigation              = models.DecimalField("irrigation in inches",
                                                  max_digits=4, decimal_places=2, default=0.0) # ##.##
    available_water_content = models.DecimalField(max_digits=4, decimal_places=2, default=0.0, # ##.##
                                                  blank=True, null=True)   # Null --> Not yet calculated

    def get_field_list(self):
        field_list = self.field_list.all()
        if field_list:
            return ', '.join([ obj.name for obj in field_list])
        else:
            return ''

    class Meta:
        verbose_name        = "Water History"
        verbose_name_plural = "Water Histories"

    def __unicode__(self):
        #return u"Water History Entry for %s %s" % (self.farm,
        #                                           #self.get_field_list, 
        #                                           self.date)
        u"%s" % self.date


#############################
### Probe & Measurements ###
#############################

class Probe(NameDesc, Comment, Audit):
    # from NameDesc:  name, description
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser

    crop_season = models.ForeignKey(CropSeason)  # Probe assignments change with crop season
    radio_id    = models.CharField(max_length=10)
    field_list  = models.ManyToManyField(Field)

    def get_field_list(self):
        field_list = self.field_list.all()
        if field_list:
            return ', '.join([ obj.name for obj in field_list])
        else:
            return ''

    def __unicode__(self):
        return u"Probe %s" % self.radio_id.strip()

    class Meta:
        unique_together = ( ("crop_season", "radio_id"), )



class ProbeReading(Audit):
    """
    Model for CSV data read from probe files
    """

    # from Audit: cdate, cuser, mdate, muser

    ## From filename
    farm_code           = models.CharField(max_length=10)
    file_date           = models.DateField()

    ## From file contents
    reading_datetime    = models.DateTimeField()
    probe_code          = models.CharField(max_length=10)
    radio_id            = models.CharField(max_length=10)
    battery_voltage     = models.DecimalField(max_digits=3, decimal_places=2) #   #.##
    battery_percent     = models.DecimalField(max_digits=5, decimal_places=2) # ###.##
    soil_potential_8    = models.DecimalField(max_digits=5, decimal_places=2) # ###.##
    soil_potential_16   = models.DecimalField(max_digits=5, decimal_places=2) # ###.##
    soil_potential_24   = models.DecimalField(max_digits=5, decimal_places=2) # ###.##
    circuit_board_temp  = models.DecimalField(max_digits=5, decimal_places=2) # ###.##
    thermocouple_1_temp = models.DecimalField(max_digits=5, decimal_places=2) # ###.##
    thermocouple_2_temp = models.DecimalField(max_digits=5, decimal_places=2) # ###.##
    minutes_awake       = models.PositiveSmallIntegerField()

    SOURCE_CHOICES = ( ('UGADB', 'UGA Database'),
                       ('User', 'User Entry'), 
                     )
    source             = models.CharField(max_length=6,
                                          choices=SOURCE_CHOICES,
                                          default="User")

    class Meta:
        verbose_name = "Raw Probe Reading"
        unique_together = ( ("radio_id", "reading_datetime", ) , )
        #ordering = [ "reading_datetime", "radio_id", ]

    def __unicode__(self):
        return u"ProbeReading %s on %s" % ( self.radio_id.strip(), 
                                            self.reading_datetime,
                                          )
    def temperature(self):
        if (0 < selt.thermocouple_1_temp < 130):
            return thermocouple_1_temp
        else:
            return thermocouple_2_temp


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
        verbose_name  = "Probe Synchronization"


    def __unicode__(self):
        return u"ProbeSync %s" % self.datetime
