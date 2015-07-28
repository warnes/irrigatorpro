from farms.models import *
from common.utils import daterange

from farms.generate_water_register import generate_water_register

from django.forms.models import modelformset_factory
from django.db.models import Q

from datetime import datetime, date, timedelta

from irrigator_pro.settings import WATER_REGISTER_DELTA

# workarounds for the absence of query datetime__date operator
from common.utils import d2dt_min, d2dt_max, d2dt_range


def getDateObject(thisDate):
    '''
    Coerce argument to class date
    '''

    if thisDate is None:
        return None
    elif isinstance(thisDate, datetime):
        return thisDate.date()
    elif isinstance(thisDate, date):
        return thisDate
    else:
        return datetime.strptime(thisDate, "%Y-%m-%d %H:%M:%S").date()



def generate_objects(wh_formset, crop_season, field, user,  report_date):

    """
    Returns the list of object for display in the template.
    Each object is an instance of the class UnifiedReport,
    defined below.

    We assume that the wh_formset is sorted by date, but not necessarily
    by source. In this implementation there are two possible sources for 
    the WaterHistory objects for one date: at most one UGA and any number
    of User.
    """

    if crop_season.season_start_date > report_date:
        return None
    
    if crop_season.season_end_date < report_date:
        report_date = crop_season.season_end_date

    generate_water_register(crop_season, field, user, None, report_date)

    water_register_query = WaterRegister.objects.filter(crop_season = crop_season, field = field)
    water_register_query = water_register_query.order_by('-datetime')
    water_register_query = water_register_query.filter(
                               Q(datetime__lte =  d2dt_min(report_date + timedelta(WATER_REGISTER_DELTA))) 
                               )

    print 
    for wr in water_register_query:
        print "Have in query: ", wr.datetime, " - ",  wr.field.pk, " - ", wr.crop_season.pk


    ### Get all the forms defined by the formset created from the water history objects
    form_index = 0
    current_form = None
    all_forms = wh_formset.forms
    ret = []

    if all_forms is not None and len(all_forms) > 0:
        current_form = all_forms[form_index]
        form_index = form_index + 1

        ## Point to the first form in the current crop season
        while current_form is not None and \
              getDateObject(current_form['datetime'].value()) is not None and \
              getDateObject(current_form['datetime'].value()) < crop_season.season_start_date:
            if form_index == len(all_forms):
                current_form = None
            else:
                #print "IF WE SEE THIS THEN THIS LOOP IS NECESSARY"
                current_form = all_forms[form_index]
                form_index = form_index + 1
                

    for day in daterange(crop_season.season_start_date, report_date + timedelta(days=1)):
        water_register = water_register_query.get(datetime__range = d2dt_range(day))
        day_record = UnifiedReport(day, water_register)

        while current_form is not None and getDateObject(current_form['datetime'].value()) == day:
            if current_form['source'].value() == "UGA":
                if day_record.uga_form is not None:
                    raise RuntimeError("There are two UGA probes defined for: " + str(day))

                day_record.add_uga(current_form)

            elif current_form['source'].value() == "User":
                day_record.all_forms.append(current_form)
            else:
                raise RuntimeError("Unrecogized source type: " + current_form['source'].value())

            if form_index == len(all_forms):
                current_form = None
            else:
                current_form = all_forms[form_index]
                form_index = form_index + 1

        ret.append(day_record)

    # Add records for days in the future
    
    ### Might want days=WATER_REGISTER_DELTA+1 below, but we don't do it
    ### in generate_water_register

    ### Also this loop could be merged with above. But this is easier to see
    ### what happens
    report_plus_delta = min(report_date + timedelta(days=WATER_REGISTER_DELTA), crop_season.season_end_date)
    
    for day in daterange(report_date + timedelta(days=1), report_plus_delta):
        print "day is: ", day
        print "Getting water register for: ", d2dt_range(day)
        water_register = water_register_query.get(datetime__range = d2dt_range(day))
        day_record = UnifiedReport(day, water_register)
        ret.append(day_record)
        
    return  ret




class UnifiedReport:
    """
    Object used for display by the template. Each object is for one calendar
    date. It contains the date and the water register for this day, in
    addition to a list of probe readings (uga_records) and a list of forms,
    each corresponding to one manual water event. The forms are extracted from
    the formset
    """


    
    def __init__(self, date, water_register):
        self.date = date
        self.water_register = water_register
        self.uga_form = None ## Only for quick check that there are not two of them.
        self.all_forms = []

    def add_uga(self, u):
        """
        Want the UGA record to be the first in the list, but 
        don't know it is the first that will be added.
        """
        self.uga_form = u
        self.all_forms[0:0] = [u]



