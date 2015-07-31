from django.db import models
from farms.models import *

class UGAProbeData(models.Model):
    id                  = models.AutoField    (db_column="data_id", primary_key=True)
    datetime            = models.DateTimeField(db_column="dt"                       ) 
    field_code          = models.IntegerField (db_column="fieldid"                  )
    node_code           = models.IntegerField (db_column="nodeid"                   )
    radio_id            = models.CharField    (db_column="netaddr", max_length=10   )
    battery_voltage     = models.FloatField   (db_column="batt"                     )
    battery_percent     = models.FloatField   (db_column="battlife"                 )
    soil_potential_8    = models.FloatField   (db_column="sm1"                      )
    soil_potential_16   = models.FloatField   (db_column="sm2"                      )
    soil_potential_24   = models.FloatField   (db_column="sm3"                      )
    circuit_board_temp  = models.FloatField   (db_column="boardtemp"                )
    thermocouple_1_temp = models.FloatField   (db_column="temp1"                    )
    thermocouple_2_temp = models.FloatField   (db_column="temp2"                    )
    minutes_awake       = models.IntegerField (db_column="awake"                    )
    __database__        = "ugatifton"

    class Meta:
        managed = False
        db_table = 'fields"."data'   # hack to access 'data' table within schema 'fields'

    def __unicode__(self):
        return u"RadioID '%s' at '%s': (%f, %f, %f) (%d, %d)" % (self.radio_id, 
                                            self.datetime, 
                                            self.soil_potential_8,
                                            self.soil_potential_16,
                                            self.soil_potential_24,
                                            self.thermocouple_1_temp,
                                            self.thermocouple_2_temp)

def get_all_radio_ids():
    """
    Return a list of all available probe radio_ids
    """
    recs = UGAProbeData.objects.values('radio_id').distinct()
    radio_ids = [ r['radio_id'] for r in recs]
    radio_ids.sort()
    return radio_ids
