from django import template
import re

from django.forms.fields import DateField
register = template.Library()

###
### Counts the total of probe readings and water history
### records (forms) in a unified_field_data.UnifiedReport record

@register.filter(expects_localtime=True)
def day_records(day_records):
    return len(day_records.uga_records) + len(day_records.forms)


@register.filter(expects_localtime=True)
def form_index(form_id):
    m = re.search( "\d+", str(form_id))
    return m.group(0)


@register.filter(expects_localtime=True)
def time_format(time_str):
    ## Easier and probably faster than dealing with Python's datetime class

    m = re.search("(\d+:\d+)", str(time_str))
    return m.group(0)

                  
