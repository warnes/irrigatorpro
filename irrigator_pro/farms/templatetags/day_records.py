from django import template

from django.forms.fields import DateField
register = template.Library()

###
### Counts the total of probe readings and water history
### records (forms) in a unified_field_data.UnifiedReport record

@register.filter(expects_localtime=True)
def day_records(day_records):
    return len(day_records.uga_records) + len(day_records.forms)

