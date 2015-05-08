from django import template

register = template.Library()
import re

@register.filter(expects_localtime=True)
def auth_id(user_id):
    return re.sub('\W', "_", str(user_id))

