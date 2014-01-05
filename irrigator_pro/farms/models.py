from django.db import models
from django.utils import timezone
from common.models import Audit, Comment, Location, NameDesc

class Farm(NameDesc, Location, Comment, Audit):
    # from NameDesc: name, description
    # from Location: address_1, address_2, city, state, zipcode, country
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    farmer      = models.ForeignKey(othermodel=User)
    users       = models.ManyToManyField(othermodel=User)


class Field(NameDesc, Location, Comment, Audit):
    # from NameDesc:  name, description
    # from Location: address_1, address_2, city, state, zipcode, country
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser

    SANDY         = 'SANDY'
    SANDY_MEDIUM  = 'SANDY/MEDIUM'
    MEDIUM_HEAVY  = 'MEDIUM/HEAVY'
    SOIL_CHOICES = ( 
        ( SANDY,           'Sandy',        ),
        ( SANDY_MEDIUM,    'Sandy/Med', ),
        ( MEDIUM_HEAVY,    'Med/Heavy', ),
    )

    farm          = models.ForeignKey(othermodel=Farm)
    acres         = PositiveSmallInteger()
    soil_type     = models.CharField(max_length=10,
                                   choices = SOIL_CHOICES,
                                   default = SANDY)

    irr_capacity  = models.PositiveSmallIntegerField()


class Crop(NameDesc, Comment, Audit):
    # from NameDesc:  name, description
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    variety     = models.CharField(max_length=32)


class CropEvent(NameDesc, Comment, Audit):
    # from NameDesc:  name, description
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    crop                    = models.ForeignKey(othermodel=Crop)
    prior_event             = models.ForeignKey(othermodel=Audit)
    days_after_prior_early  = models.SmallPositiveInteger()
    days_after_prior_normal = models.SmallPositiveInteger()    
    days_after_prior_late   = models.SmallPositiveInteger()    


class Planting(NameDesc, Comment, Audit):
    # from NameDesc:  name, description
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    fields            = models.ManyToMany(othermode=Field)
    crop              = models.ForeignKey(othermodel=Crop)


class PlantingEvents(Comment, Audit):
    # from Comment: comment
    # from Audit: cdate, cuser, mdate, muser
    planting          = models.ForeignKey(othermodel=Planting)
    event             = models.ForeignKey(othermodel=CropEvent)
    event_date        = models.DateField()



    
