import decimal

from common.models import Audit, Comment, Location, Location_Optional, NameDesc

from datetime import date, datetime, time, timedelta
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
    earliest_changed_dependency_date = models.DateField(blank=True,
                                        null=True,
                                        verbose_name="Earliest date in modified WaterRegister dependencies"
                                        )


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

##########################################
### CropSeason (Crop + Season + Fields) ##
##########################################

def get_default_cropseason_start():
    return timezone.now()

def get_default_cropseason_end():
    return timezone.now() + timedelta(days=154)

class CropSeason(NameDesc, Comment, Audit):
    # from NameDesc:  name, description
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    season_start_date = models.DateField(default=get_default_cropseason_start,
                                         verbose_name="Season Start Date",
                                         )
    season_end_date = models.DateField(default=get_default_cropseason_end,
                                       verbose_name="Approximate Season End Date",
                                      ) ## UI needs to set this relative
                                        ## to the user-provied
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

def get_default_cropseasonevent_date():
    return timezone.now()

class CropSeasonEvent(Comment, Audit):
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    crop_season = models.ForeignKey(CropSeason)
    field       = models.ForeignKey(Field)
    crop_event  = models.ForeignKey(CropEvent)
    date        = models.DateField(default=get_default_cropseasonevent_date)

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



#############################
### Probe & Measurements ###
#############################

class Probe(NameDesc, Comment, Audit):
    # from NameDesc:  name, description
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser

    crop_season = models.ForeignKey(CropSeason,   blank=False)  # Probe assignments change with crop season
    radio_id    = models.CharField(max_length=10, blank=False)  # don't allow blanks!
    field       = models.ForeignKey(Field)

    def __unicode__(self):
        return u"Probe %s" % self.radio_id.strip()

    class Meta:
        unique_together = ( ("crop_season", "radio_id"), )



###############################################################
### Abstract base probe reading, which for now is the base for
### ProbeReading, WaterHistory, WaterRegister, and UnifiedTable
###############################################################

SOURCE_CHOICES = ( 
    ('UGA',      'UGA Database'),
    ('User',     'User Entry'),
    ('Computed', 'Computed'),
    ('Unknown',  'Unknown'),
    )

class FieldDataReading(Audit, Comment):
    #  All temperatures are stored in degrees Farenheit
    #  All depths are stored in inches
    #  All pressures are in kilopascals (kPa) == centibar (100 bar)

    source             = models.CharField(max_length=8,
                                          choices=SOURCE_CHOICES,
                                          default='User'
                                          )

    datetime            = models.DateTimeField(blank=False, null=False)

    min_temp_24_hours   = models.DecimalField(max_digits=5, decimal_places=2, # ###.##
                                              blank=True, null=True,
                                              verbose_name='Minimum temperature in last 24 hours in degrees Farenheit') 
    
    max_temp_24_hours   = models.DecimalField(max_digits=5, decimal_places=2, # ###.##
                                              blank=True, null=True,
                                              verbose_name='Maximum temperature in last 24 hours in degrees Farenheit') 


    ignore              = models.BooleanField(default=False, blank=True)


    soil_potential_8    = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) # ###.##
    soil_potential_16   = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) # ###.##
    soil_potential_24   = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) # ###.##

    rain                = models.DecimalField("Rainfall in inches", blank = True,
                                              max_digits=4, decimal_places=2, default=0.0) # ##.##
    irrigation          = models.DecimalField("Irrigation in inches", blank = True,
                                              max_digits=4, decimal_places=2, default=0.0) # ##.##

    ## These property function allow treating 'date' and 'time' as
    ## fields, which automagically get/set the components of
    ## self.datetime
    @property 
    def date(self):
        if self.datetime:
            return self.datetime.date()
        else:
            return None

    @date.setter
    def date(self, value):
        if self.datetime:
            self.datetime = datetime.combine( value, self.datetime.time() )
        else:
            self.datetime = datetime.combine( value, time.min )            

    @property
    def time(self):
        if self.datetime:
            return self.datetime.time()
        else:
            return None

    @time.setter
    def time(self, value):
        if self.datetime:
            self.datetime = datetime.combine( self.datetime.date(), value)
        else:
            self.datetime = datetime.combine( date.today(), value)            

    class Meta:
        abstract = True

###############################################################
### Abstract class holding 'crop season' and 'field' for use by 
### WaterHistory, WaterRegister, and UnifiedTable
###############################################################


class CropSeasonField(models.Model):
    """
    Class to hold 'crop_season' and 'field' for use in WaterHistory
    and WaterRegister 
    """
    crop_season             = models.ForeignKey(CropSeason)
    field                   = models.ForeignKey(Field)

    class Meta:
        abstract = True



####################
### ProbeReading ###
####################

class ProbeReading(FieldDataReading):
    """
    Model for CSV data read from probe files
    """

    def __init__(self, *args, **kwargs): 
        '''
        Change the default value of 'source' to 'UGA'
        '''
        super(ProbeReading, self).__init__(*args, **kwargs) 
        self._meta.get_field('source').default = 'UGA'

    # from Audit: cdate, cuser, mdate, muser
    # from FieldDataReading: datetime, date*, time*, min_temp_24_hours,
    #                        max_temp_24_hours, ignore, 
    #                        soil_potential_8, soil_potential_16,
    #                        soil_potential_24, rain, irrigation

    ## From filename
    farm_code           = models.CharField(max_length=10, blank=True)
    file_date           = models.DateField(blank=True, null=True)

    ## From file contents
    probe_code          = models.CharField(max_length=10, blank=True)
    radio_id            = models.CharField(max_length=10)
    battery_voltage     = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True) #   #.##
    battery_percent     = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True) # ###.##
    circuit_board_temp  = models.DecimalField(max_digits=5, decimal_places=2, # ###.##
                                              blank=True, null=True,
                                              verbose_name='Circuit Board Temperature in Degrees Celcius') 
    thermocouple_1_temp = models.DecimalField(max_digits=5, decimal_places=2, # ###.##
                                              blank=True, null=True,
                                              verbose_name='Thermocouple 1 Temperature in Degrees Celcius') 
    thermocouple_2_temp = models.DecimalField(max_digits=5, decimal_places=2, # ###.##
                                              blank=True, null=True,
                                              verbose_name='Thermocouple 2 Temperature in Degrees Celcius') 
    minutes_awake       = models.PositiveSmallIntegerField(blank=True, null=True)


    class Meta:
        verbose_name = "Probe Reading"
        unique_together = ( ("radio_id", "datetime", ) , )
        #ordering = [ "datetime", "radio_id", ]

    def __unicode__(self):
        return u"ProbeReading %s on %s" % ( self.radio_id.strip(),
                                            self.datetime,
                                          )
    def temperature(self):
        if (0 < self.thermocouple_1_temp < 130):
            return thermocouple_1_temp
        else:
            return thermocouple_2_temp

####################
### WaterHistory ###
####################

class WaterHistory(CropSeasonField, FieldDataReading):

    def __init__(self, *args, **kwargs): 
        '''
        Change the default value of 'source' to 'User'
        '''
        super(WaterHistory, self).__init__(*args, **kwargs) 
        self._meta.get_field('source').default = 'User'


    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    # from FieldDataReading: datetime, date*, time*, min_temp_24_hours,
    #                        max_temp_24_hours, ignore, 
    #                        soil_potential_8, soil_potential_16,
    #                        soil_potential_24, rain, irrigation

    class Meta:
        verbose_name        = "Water History"
        verbose_name_plural = "Water Histories"

    def __unicode__(self):
        return u"Water History Entry [%s] for %s" % ( self.id , self.datetime ) 


#################################################################################
### WaterRegisterFields abstract class to hold fields used by both WaterHistory
### and UnifiedTable
#################################################################################

class WaterRegisterFields(FieldDataReading):
    """
    Fields for computed available water content
    """

    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    # from FieldDataReading: datetime, date*, time*, 
    #                        min_temp_24_hours,
    #                        max_temp_24_hours,
    #                        ignore, 
    #                        soil_potential_8, soil_potential_16,
    #                        soil_potential_24, 
    #                        rain, irrigation

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
        abstract = True

######################
### Water Register ###
######################

class WaterRegister(CropSeasonField, WaterRegisterFields):

    def __init__(self, *args, **kwargs): 
        '''
        Change the default value of 'source' to 'Computed'
        '''
        super(WaterRegister, self).__init__(*args, **kwargs) 
        self._meta.get_field('source').default = 'Computed'

    class Meta:
        verbose_name = "Water Register"
        unique_together = ( ("crop_season", "field", "datetime"), )
        ordering        =   ("crop_season", "field", "datetime")

    def __unicode__(self):
        return u"Water Register for %s - %s - %s" % (self.crop_season, 
                                                     self.field, 
                                                     self.datetime)

# #####################
# ### Unified Table ###
# #####################

# class UnifiedTable(CropSeasonField, WaterRegisterFields):
#     """
#     Model to hold concatinated outer joins of
#         WaterRegister x WaterHistory and  
#         WaterRegister x ProbeReading 
#     for creation of the unified data entry and water register page
#     """
#     waterregister = models.ForeignKey(WaterRegister, blank=False)
#     waterhistory  = models.ForeignKey(WaterHistory,  blank=True)
#     probereading  = models.ForeignKey(ProbeReading,  blank=True)

#     pr_source     = models.CharField(max_length=8,
#                                      choices=SOURCE_CHOICES,
#                                      default='Unknown'
#                                      )
#     wh_source     = models.CharField(max_length=8,
#                                      choices=SOURCE_CHOICES,
#                                      default='Unknown'
#                                      )
#     wr_source     = models.CharField(max_length=8,
#                                      choices=SOURCE_CHOICES,
#                                      default='Unknown'
#                                      )

    
#     pr_datetime   = models.DateTimeField(blank=True, null=True)
#     wh_datetime   = models.DateTimeField(blank=True, null=True)
#     wr_datetime   = models.DateTimeField(blank=True, null=True)


#     class Meta:
#         verbose_name        = "Unified Table Entry"
#         verbose_name_plural = "Unified Table Entries"
#         unique_together     = ( ("crop_season", "field", "source", "datetime"), )
#         ordering            =   ("crop_season", "field", "source", "datetime")
#         managed             = False 


#################
### ProbeSync ###
#################

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


###################
### InvitedUser ###
###################

class InvitedUser(NameDesc, Audit):
    email       = models.EmailField(unique = True)
    farms        = models.ManyToManyField(Farm)

    def __unicode__(self):
        return self.email
