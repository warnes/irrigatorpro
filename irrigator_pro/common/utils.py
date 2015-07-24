from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.utils import timezone

import math

min_time = time.min
min_time = min_time.replace(tzinfo =  timezone.get_current_timezone())

max_time = time.max
max_time = max_time.replace(tzinfo =  timezone.get_current_timezone())



def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(days=n)


def safelog( val ):
    if val <= 0:
        return float("-inf")
    else:
        return math.log( float(val) )

def d2dt_min(date):
    """
    Date to DateTime (Min)
    
    Constructs lower bound for date to work around the absence of a
    datetime__date operator.
    
    This is what we *want* to do:
         .filter(datetime__date__lte=date)
    but this is not supported until django 1.9, so for now we need to do
         .fiter(datetime__lte=d2dt_min(date))
    """
    return datetime.combine(date, min_time)


def d2dt_max(date):
    """
    Date to DateTime (Min)
    
    Constructs upper bound for date to work around the absence of a
    datetime__date operator.
    
    This is what we *want* to do:
         .filter(datetime__date__gte=date)
    but this is not supported until django 1.9, so for now we need to do
         .fiter(datetime__gte=d2dt_max(date))
    """
    return datetime.combine(date, max_time)



def d2dt_range(date):
    """
    Date to DateTime Range

    Constructs upper and lower ranges for the specified date to work
    around the absence of datetime__date query operattor.

    This is what we *want* to do:
         .filter(datetime__date=date)
    but this is not supported until django 1.9, so for now we need to do
         .fiter(datetime__rage=d2dt_range(date))
    """
    return  ( datetime.combine(date, min_time), \
              datetime.combine(date, max_time) \
             )



def minNone(*values):

    """
    In python None is considered smaller than any number, and a min on a list
    containing None will return None, which is not what we want.
    """

    if not values or len(values) == 0:
        return None

    not_none = [x for x in values if x is not None]
    if len(not_none)==0:
        return None

    return min(not_none)


def quantize( f ):
    """ Convert to a Decimal with resolution of 0.01 """
    # An issue within the python Decimal class causes conversion from
    # Decimal to Decimal to fail if the module is reloaded.  Work
    # around that issue by converting to string, then to a Decimal.
    retval = Decimal(str(f)).quantize( Decimal('0.01') )

    return retval


## Tests
if True: #False:
    dt = date(2014,01,05)
    print dt
    print d2dt_min(dt)
    print d2dt_range(dt)
