from django import template
from sys import stdout, stderr

register = template.Library()

@register.simple_tag(takes_context=True)
def object_name(context):
    
    print stderr, "dir=", dir(context); stderr.flush()
    print stderr, "dicts=", context.dicts; stderr.flush()
    print stderr, "has_key('object')", context.has_key('object'); stderr.flush()

    if context.has_key('object'):
        obj = context['object']
    elif context.has_key('instance'):
        obj = context['instance']
    else:
        raise("Context has neither 'object' nor 'instance' key.")

    if hasattr(obj, "_meta") and hasattr(obj._meta, "verbose_name"):
        return obj._meta.verbose_name
    else:
        return obj.__class__.__name__.replace("_", " ").title()

@register.simple_tag(takes_context=True)
def object_name_plural(context):

    if context.has_key('object'):
        obj = context['object']
    elif context.has_key('instance'):
        obj = context['instance']
    else:
        raise("Context has neither 'object' nor 'instance' key.")

    if hasattr(obj, "_meta") and hasattr(obj._meta, "verbose_name_plural"):
        return obj._meta.verbose_name_plural
    else:
        name = object_name(context)
        if name.endswith("y"):
            return name[:-1] + "ies"
        else:
            return name + "s"
