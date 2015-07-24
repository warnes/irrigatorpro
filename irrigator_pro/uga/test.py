from django.test      import TestCase
from farms.models     import *
from uga.models       import *
from datetime         import date, datetime, time, timedelta
from django.db.models import Count
from uga.aggregates   import *

field = Field.objects.get(name='East 1')
cs    = CropSeason.objects.get(name='Corn 2015', field_list=field)
day   = date.today()
user  = User.objects.get(email='greg@warnes.net')
today = date.today()


# Add a few records to the UGAProbeReading table so we have something to query
probes = Probe.objects.filter(crop_season=cs, field=field).distinct()
radio_ids = map(lambda x:x['radio_id'], probes.values('radio_id') )

sql1 = """
SELECT DISTINCT ON (dt::date)
  data_id, dt, dt::date AS date, fieldid, nodeid, netaddr, batt, battlife, sm1, sm2, sm3, awake
FROM
  fields.data
WHERE
  ( dt::date BETWEEN '%(start_date)s' AND '%(end_date)s' )
AND
  netaddr IN ( %(radio_ids)s ) 
ORDER BY
  dt::date DESC, dt DESC
"""
  
radio_id_str = ", ".join( [ "'%s'" % x for x in radio_ids ] )

query1 = UGAProbeData.objects.raw(sql1 % {'start_date': cs.season_start_date,
                                        'end_date'  : cs.season_end_date,
                                        'radio_ids' : radio_id_str
                                        }  
                                 ) 

##print query1.query.sql

sql2 = """
SELECT 
  MAX(data_id) as data_id,
  dt::date as date, 
  MAX(temp1) AS max_temp_24_hours,
  MIN(temp2) AS min_temp_24_hours
FROM
  fields.data
WHERE
  ( dt::date BETWEEN '%(start_date)s' AND '%(end_date)s' )
AND
  netaddr IN ( %(radio_ids)s ) 
GROUP BY
  dt::date
"""

query2 = UGAProbeData.objects.raw(sql2 % {'start_date': cs.season_start_date,
                                        'end_date'  : cs.season_end_date,
                                        'radio_ids' : radio_id_str
                                        } 
                                 ) 

##print query2.query.sql

sql_join = """
SELECT 
  a.*, 
  b.max_temp_24_hours, 
  b.min_temp_24_hours
FROM 
  (
  %s
  ) AS a
LEFT JOIN 
  (
  %s
  ) AS b
ON 
  a.date = b.date
""" % ( query1.query.sql, query2.query.sql)

query_join = UGAProbeData.objects.raw(sql_join)

common_fields = [ 'datetime', 
                  'max_temp_24_hours', 
                  'min_temp_24_hours',
                  'soil_potential_8',
                  'soil_potential_16', 
                  'soil_potential_24',
                  ]



for upd in query_join:
    (wh, created) = WaterHistory.objects.get_or_create(crop_season=cs,
                                                       field=field,
                                                       datetime__gte=datetime.combine(upd.date, time.min),
                                                       datetime__lte=datetime.combine(upd.date, time.max),
                                                       source="UGA",
                                                       defaults = { 'cuser': user,
                                                                    'cdate': datetime.now(),
                                                                    'muser': user,
                                                                    'mdate': datetime.now(),
                                                                    'datetime':upd.datetime,
                                                                    }
                                                       )

    for field in common_fields:
        val = getattr(upd, field)
        print field, ": ", val, " (", type(val), ")"
        setattr(wh, field, val)
        print "--"

    print wh.soil_potential_24

    print "??"
    wh.source = 'UGA'
    print "!!"

    print "upd.datetime", upd.datetime, " (", type(upd.datetime), ")"

    wh.save()
