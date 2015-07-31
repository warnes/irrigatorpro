from django import template
from datetime import date, datetime, timedelta

register = template.Library()

@register.filter(expects_localtime=True)
def is_today(value):
    if isinstance(value, datetime):
        value = value.date()
    return value == date.today()

@register.filter(expects_localtime=True)
def is_past(value):
    if isinstance(value, datetime):
        value = value.date()
    return value < date.today()

@register.filter(expects_localtime=True)
def is_future(value):
    if isinstance(value, datetime):
        value = value.date()    
    return value > date.today()

@register.filter(expects_localtime=True)
def compare_today(value):
    if isinstance(value, datetime):
        value = value.date()
    return value - date.today()

@register.filter(expects_locattime=True)
def today_in_season(season):
    start_date = season.season_start_date
    end_date   = season.season_end_date
    return (start_date <= date.today() <= end_date)
        
