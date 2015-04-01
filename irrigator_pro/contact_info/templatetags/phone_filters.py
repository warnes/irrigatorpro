from django import template

register = template.Library()

@register.filter(expects_localtime=True)
def us_number(value):
    if (len(value) != 10):
        return value
    return "(" + value[0:3] + ") " + value[3:6] + "-" + value[6:10]


