from django.test      import TestCase
from farms.models     import *
from uga.models       import *
from datetime         import date, datetime, time, timedelta
from django.db.models import Count
from django.utils     import timezone # for make_aware, get_default_timezone
from uga.aggregates   import *
from django.contrib.auth.models import User

field = Field.objects.get(name='East 1')
cs    = CropSeason.objects.get(name='Corn 2015', field_list=field)
day   = date.today()
user  = User.objects.get(email='greg@warnes.net')
today = date.today()


def to_tz(datetime):
    return timezone.make_aware( datetime, timezone.get_default_timezone() )


def pull_probes_by_cropseason_field(crop_season, field, user=None):
    """
    Query the UGA database and pull relevant probe summary data into
    the WaterHistory table for the specified crop season and field.  

    Returns a list contiaing the created/updated water records

    This is accompished by:
    1. Identifying probes assigned to this cropseason and field
    2. Identifying the time period covered by this cropseason 
    3. Running a query on the UGA probe database that captures _for
       each date_: 
          a) The soil potential readings from the last record on that
             date
          b) The minimum and maximum soil temperature readings
    4. Copying this information into a WaterHistory records for each
       date, overwriting any existing records for that date.

    Assumptions:
    1. UGA Probe Readings are write-once, delete-never, so we don't
       need to worry about the dates of individual probe readings
       changing.

    TODO:
    1. When a probe is reassigned, delete the relevant WaterHistory
       records
    """

    if not isinstance(crop_season, CropSeason):
        crop_season = CropSeason.objects.get(pk=crop_season)

    if not isinstance(field, Field):
        field= Field.objects.get(pk=field)

    if user is None:
        user = User.objects.filter(username='SyncProcess').first()
        if user is None:
           user = User.objects.create_user(username='SyncProcess',
                                           email='webmaster@irrigatorpro.org')
    
    # Get the RadioIDs to query
    probes = Probe.objects.filter(crop_season=crop_season, field=field).distinct()
    radio_ids = map(lambda x:x['radio_id'], probes.values('radio_id') )

    # return if nothing to do
    if len(probes) == 0:
        return [{}]
    
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
    
    query1 = UGAProbeData.objects.raw(sql1 % {'start_date': crop_season.season_start_date,
                                            'end_date'  : crop_season.season_end_date,
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
    
    query2 = UGAProbeData.objects.raw(sql2 % {'start_date': crop_season.season_start_date,
                                            'end_date'  : crop_season.season_end_date,
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
    
    accum = []
    for upd in query_join:
        (wh, created) = WaterHistory.objects.get_or_create(
            crop_season=crop_season,
            field=field,
            datetime__gte=to_tz(datetime.combine(upd.date, time.min)),
            datetime__lte=to_tz(datetime.combine(upd.date, time.max)),
            source="UGA",
            defaults = { 'cuser': user,
                         'cdate': timezone.now(),
                         'muser': user,
                         'mdate': timezone.now(),
                         'datetime':upd.datetime,
                         }
            )
    
        wh.source = 'UGA'
        wh.crop_season       = crop_season
        wh.field             = field
        wh.datetime          = to_tz(upd.datetime) 
        wh.max_temp_24_hours = upd.max_temp_24_hours
        wh.min_temp_24_hours = upd.min_temp_24_hours
        wh.soil_potential_8  = upd.soil_potential_8
        wh.soil_potential_16 = upd.soil_potential_16
        wh.soil_potential_24 = upd.soil_potential_24
        wh.rainfall          = 0
        wh.irrigation        = 0
        
        if wh.ignore is None:   # Don''t overwrite ignore flag 
            wh.ignore = False

        if wh.pk is None:       # if wh is newly created
            wh.cuser             = user
            wh.cdate             = timezone.now()

        wh.muser             = user
        wh.mdate             = timezone.now()
    
        wh.save()
        accum.append( wh )
    
    return accum


def pull_probes_by_period(start_date=None, end_date=None, user=None):
    """
    Query the UGA database and pull relevant probe summary data into
    the WaterHistory table for fields in crop seasons that overlap the
    specified date interval.

    Returns a list contiaing the created/updated water records

    If omitted or None, start_date defaults to datetime.min.
    If omitted or None, end_date   defaults to datetime.max.
    """
    if start_date is None:
        start_date = date.min
    elif isinstance(start_date, datetime):
        start_date = start_date.date()

    if end_date is None:
        end_date = date.max
    elif isinstance(end_date, datetime):
        end_date = end_date.date()

    csDictList = CropSeason.objects.filter(
        # season startes before period ends
        season_start_date__lte = end_date,
        # season ends after period starts
        season_end_date__gte   = start_date
        ).values('id', 'name', 'field_list').distinct()

    # csDictList has one record for each CropSeason, Field pair
    # overlapping the provided date.
    accum = []
    for csDict in csDictList:
        accum.extend( pull_probes_by_cropseason_field(crop_season=csDict['id'],
                                                      field=csDict['field_list'],
                                                      user=user) )
    return accum


if __name__ == "__main__":
    start_time = timezone.now()
    ret = pull_probes_by_cropseason_field(crop_season=cs, field=field)
    print "One CropSeason + field took %s seconds to update %d WaterHistory records" % ( 
        timezone.now() - start_time,
        len(ret)
        )
    
    start_time = timezone.now()
    ret = pull_probes_by_period( date.today(), date.today() )
    print "All current cropseasons + fields took %s seconds to update %d WaterHistory records" % ( 
        timezone.now() - start_time,
        len(ret)
        )
    
