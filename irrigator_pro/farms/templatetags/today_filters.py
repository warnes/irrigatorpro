from django import template
from datetime import date, timedelta

register = template.Library()

@register.filter(expects_localtime=True)
def is_today(value):
    return value == date.today()

@register.filter(expects_localtime=True)
def is_past(value):
    return value < date.today()

@register.filter(expects_localtime=True)
def is_future(value):
    return value > date.today()

@register.filter(expects_localtime=True)
def compare_today(value):
    return value - date.today()
