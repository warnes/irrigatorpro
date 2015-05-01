import decimal


from common.models import Audit, Comment, Location, Location_Optional, NameDesc

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

import sys

                                    
############
## Display user email name instead of username when selecting users
############
def user_unicode_patch(self):
    return u"%s, %s (%s)" % (self.last_name.capitalize(), 
                             self.first_name.capitalize(), 
                             self.email)

User.__unicode__ = user_unicode_patch


############
## Patch problem with Decimal field
############

def to_python(self, value):
    if value is None:
        return value
    try:
        return decimal.Decimal(str(value))
    except decimal.InvalidOperation:
        raise exceptions.ValidationError(
            self.error_messages['invalid'],
            code='invalid',
            params={'value': value},
        )


models.DecimalField.to_python = to_python


############
### Farm ###
############

class Farm(NameDesc, Location_Optional, Comment, Audit):
    # from NameDesc: name, description
    # from Location: address_1, address_2, city, state, zipcode, country
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    farmer        = models.ForeignKey(User, related_name="farmers")
    users         = models.ManyToManyField(User, blank=True, verbose_name="Authorized Users")
    gps_latitude  = models.FloatField("GPS Latitude",  blank=True, null=True)
    gps_longitude = models.FloatField("GPS Longitude", blank=True, null=True)	
    
    def get_farmer_and_user_list(self):
        retval = [self.farmer.pk] + map(lambda x: x.pk, self.users.all())
        return retval

    def get_farmer_and_user_objects(self):
        retval = [self.farmer] + map(lambda x: x, self.users.all())
        return retval



    def get_users(self):
        user_list = self.users.all()
        if user_list:
            return ', '.join([ obj.email for obj in user_list])
        else:
            return ''


    def get_fields(self):
        if len(self.attached_fields) == 0:
            self.attached_fields = Field.objects.filter(farm = self)
    
        return self.attached_fields

    def __init__(self, *args, **kwargs):
        super(Farm, self).__init__(*args, **kwargs)
        self.attached_fields = []
    

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
                                        decimal_places=2,
                                        validators=[MinValueValidator(Decimal('0.01'))]) # ###.##
    soil_type     = models.ForeignKey('SoilType')
    irr_capacity  = models.DecimalField(max_digits=3,
                                        verbose_name='Irrigation Capacity (per 24 hours)',
                                        decimal_places=2,
                                        validators=[MinValueValidator(Decimal('0.01'))]) # ###.##

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
        verbose_name = "Soil Type Parameter"


############
### Crop ###
############

class Crop(NameDesc, Comment, Audit):
    # from NameDesc:  name, description
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    variety            = models.CharField(max_length=32,
                                          blank=True,
                                          help_text="Crop variety.  Use 'All' for no specific variety."
                                         )
    season_length_days = models.PositiveSmallIntegerField(verbose_name="Season Length (days)")

    max_root_depth     = models.PositiveSmallIntegerField(default=18,
                                                          verbose_name="Maximum Root Depth (inches)"
                                                         )

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.variety)

    class Meta:
        ordering = ['name']


class CropEvent(NameDesc, Comment, Audit):
    # from NameDesc:  name, description
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    crop               = models.ForeignKey(Crop)
    order              = models.PositiveSmallIntegerField(help_text="Events will be displayed in the order given by this (integer) value. Must be unique.")
    duration           = models.PositiveSmallIntegerField(help_text="length of this event (days)")

    daily_water_use    = models.DecimalField(max_digits=3,
                                             decimal_places=2,
                                             help_text="Water absorbed by crop each day (inches)"
                                             )
    max_temp_2in       = models.DecimalField(max_digits=3, 
                                             decimal_places=0,
                                             blank=True,
                                             null=True,
                                             verbose_name="Temp threshold at 2in",
                                             help_text="Maximum allowed soil temperature at 2 inch depth (Farenheit)"
                                             )

    key_event          = models.BooleanField(default=False, 
                                             help_text="Always display to user in crop event list")
    irrigate_to_max    = models.BooleanField(default=False, 
                                             help_text="Irrigate to Max AWC then no more through harvest") 
    do_not_irrigate    = models.BooleanField(default=False, 
                                             help_text="Do not irrigate regardless of Average Water Content and Temperature") 

    irrigation_message = models.TextField(blank=True,
                                          help_text="Message to display on Water Register")

    def __unicode__(self):
        return self.name
        #return u"%s: %s" % (self.crop, self.name)

    class Meta:
        ordering = [ 'crop__name', 'order', ]
        verbose_name = "Crop Event"
        unique_together = ( ("crop", "order"), )

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
                                         )
    season_end_date = models.DateField(default=timezone.now() + timedelta(days=154),
                                       verbose_name="Approximate Season End Date",
                                      ) ## UI needs to increment
                                        ## this off of user-provied
                                        ## season_start_date

    crop              = models.ForeignKey(Crop)
    field_list        = models.ManyToManyField(Field)

    def crop_season_year(self):
        return season_start_date.year

    def get_field_list(self):
        field_list = self.field_list.all()
        if field_list:
            return ', '.join([ str(obj) for obj in field_list])
        else:
            return ''

    def __unicode__(self):
        return self.name

    # Ensure each field has a full set of CropSeasonEvents, creating if necessary
    def save(self, *args, **kwargs):
        super(CropSeason, self).save(*args, **kwargs) # Call the "real" save() method.

        # get the list of crop events for this crop (once!)
        crop_events = CropEvent.objects.filter(crop = self.crop).order_by("order")

        # delete events that (no longer) match field list or crop 
        self.delete_orphan_events()

        # get the list of all existing crop_season_events for this crop_season
        crop_season_events = CropSeasonEvent.objects.filter(crop_season=self)

        for field in self.field_list.all():
            # get any events that already exist for this field
            field_events = crop_season_events.filter(field = field)

            prev_end_date = self.season_start_date;
            for ce in crop_events:
                matches = field_events.filter(crop_event=ce).count()
                if not matches:
                    cse = CropSeasonEvent(crop_season=self,
                                         field=field,
                                         crop_event=ce,
                                         date = prev_end_date,
                                         cdate = timezone.now(),
                                         cuser = self.muser,
                                         mdate = timezone.now(),
                                         muser = self.muser
                                     )
                    cse.save()
                    prev_end_date += timedelta(days=ce.duration)


    def delete_orphan_events(self, all=False):
        """
        Delete CropSeasonEvents for which there is no matching field
        in CropSeason.field_list, and for events that don't match
        crop_season.crop.
        """
        if all:
            crop_season_list = CropSeason.objects.all()
        else: 
            crop_season_list = [ self ]

        for crop_season in crop_season_list:
            field_list = crop_season.field_list.all()

            # Get all events that map to this crop_season
            events = CropSeasonEvent.objects.filter(crop_season=crop_season)

            # Delete events with fields that are not listed in crop_season.field_list
            events.exclude(field=field_list).delete()

            # Delete events that don't match crop_season.crop
            events.exclude(crop_event__crop=crop_season.crop).delete()


    class Meta:
        ordering = [ 'season_start_date', 'crop' ]
        verbose_name = 'Crop Season'


class CropSeasonEvent(Comment, Audit):
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    crop_season = models.ForeignKey(CropSeason)
    field       = models.ForeignKey(Field)
    crop_event  = models.ForeignKey(CropEvent)
    date        = models.DateField(default=timezone.now())

    def get_event_duration(self):
        return self.crop_event.duration

    def get_event_order(self):
        return self.crop_event.order

    def get_event_description(self):
        return self.crop_event.description

    def get_key_event(self):
        return self.crop_event.key_event

    class Meta:
        verbose_name = "CropSeason Event"

    def __unicode__(self):
        return self.crop_event.name

    class Meta:
        unique_together = ( ("crop_season", "field", "crop_event", ) , )
        ordering = [ 'field', 'crop_event__order' ]
        verbose_name = "Crop Season Event"


#############
### Water ###
#############

class WaterHistory(Comment, Audit):
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    crop_season             = models.ForeignKey(CropSeason)
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
        return u"Water History Entry for [%s] on %s" % (self.get_field_list(), self.date)


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
            return ', '.join([ str(obj) for obj in field_list])
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
    farm_code           = models.CharField(max_length=10, blank=True)
    file_date           = models.DateField(blank=True, null=True)

    ## From file contents
    reading_datetime    = models.DateTimeField()
    probe_code          = models.CharField(max_length=10, blank=True)
    radio_id            = models.CharField(max_length=10)
    battery_voltage     = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True) #   #.##
    battery_percent     = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True) # ###.##
    soil_potential_8    = models.DecimalField(max_digits=5, decimal_places=2) # ###.##
    soil_potential_16   = models.DecimalField(max_digits=5, decimal_places=2) # ###.##
    soil_potential_24   = models.DecimalField(max_digits=5, decimal_places=2) # ###.##
    circuit_board_temp  = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True) # ###.##
    thermocouple_1_temp = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True) # ###.##
    thermocouple_2_temp = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True) # ###.##
    minutes_awake       = models.PositiveSmallIntegerField(blank=True, null=True)

    SOURCE_CHOICES = ( ('UGADB', 'UGA Database'),
                       ('User', 'User Entry'),
                     )
    source             = models.CharField(max_length=6,
                                          choices=SOURCE_CHOICES,
                                          default="User")

    

    class Meta:
        verbose_name = "Probe Reading"
        unique_together = ( ("radio_id", "reading_datetime", ) , )
        #ordering = [ "reading_datetime", "radio_id", ]

    def __unicode__(self):
        return u"ProbeReading %s on %s" % ( self.radio_id.strip(),
                                            self.reading_datetime,
                                          )
    def temperature(self):
        if (0 < self.thermocouple_1_temp < 130):
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
        verbose_name  = "Probe Data Synchronization"


    def __unicode__(self):
        return u"ProbeSync %s" % self.datetime


######################
### Water Register ###
######################

class WaterRegister(Audit):
    """
    Model for computed available water content
    """

    # from Audit: cdate, cuser, mdate, muser

    # Fields specifying the Field
    crop_season           = models.ForeignKey(CropSeason)
    field                 = models.ForeignKey(Field)
    date                  = models.DateField()

    # Fields copied from CropEvent records
    crop_stage            = models.CharField(max_length=32) # CropEvent.name
    daily_water_use       = models.DecimalField(max_digits=3, decimal_places=2) # #.##
    max_temp_2in          = models.DecimalField(max_digits=3, decimal_places=0, blank=True, null=True,
                                                verbose_name="Temp threshold at 2in",
                                                help_text="Maximum allowed soil tempoerature at 2 inch depth (Farenheit)"
                                                )
    do_not_irrigate      = models.BooleanField(default=False, 
                                               help_text="Do not irrigate regardless of Average Water Content and Temperature"
                                               ) 
    message               = models.TextField(blank=True)
    irrigate_to_max       = models.BooleanField(default=False)
    
    # Fields copied from WaterRecord records
    rain                  = models.DecimalField(max_digits=3, decimal_places=2, blank=True) # #.##
    irrigation            = models.DecimalField(max_digits=3, decimal_places=2, blank=True) # #.##

    # Calculated fields - Numeric
    average_water_content = models.DecimalField(max_digits=4, decimal_places=2) # ##.##
    max_observed_temp_2in = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True) # ###.#

    # Calculated fields - Boolean
    computed_from_probes  = models.BooleanField(default=False)
    irrigate_flag         = models.BooleanField(default=False)
    too_hot_flag          = models.BooleanField(default=False)
    check_sensors_flag    = models.BooleanField(default=False)
    dry_down_flag         = models.BooleanField(default=False)

    # Field tracking status of irrigate_to_max, based on previous wr records and crop events.

    irrigate_to_max_seen = models.BooleanField(default=False)
    irrigate_to_max_achieved = models.BooleanField(default=False)

    # Days to watering. Established using future records.

    days_to_irrigation  = models.SmallIntegerField(default = -1)


    class Meta:
        verbose_name = "Water Register"
        unique_together = ( ("crop_season", "field", "date"), )
        ordering        = ("crop_season", "field", "date")

    def __unicode__(self):
        return u"%s - %s - %s" % ("crop_season", "field", "date")





class InvitedUser(NameDesc, Audit):
    email       = models.EmailField()
    farms        = models.ManyToManyField(Farm)

    def __unicode__(self):
        return self.email
