from sys import stdout, stderr
from farms.models import Farm, Planting
from django.db.models import Q
from django.template import Library, Node, TemplateSyntaxError, resolve_variable

register = Library()

class ContextNode(Node):
  def __init__(self, func):
    self.func = func

  def render(self, context):
    print "In ContextNode"
    return self.func(context) 

# @register.tag
# def some_tag(parser, tokens):
#   bits = token.split_contents()
#   tag = bits.pop(0) # pop tag
#   context_var = None

#   if len(bits):
#     context_var = bits.pop(0)

#   user_var = bits.pop()

#   # This is a wrapper function to accept the context variable
#   def some_tag_wrap(context):
#     context[context_var] = SomeModel.objects.filter(user = resolve_variable(user_var, context))
#     return ''

#   return ContextNode(some_tag_wrap) 

@register.tag
def farm_list(parser, token):
    """
    Return a list of all Farm objects corresponding to request.user
    """

    print "In farm_list tag"

    def farm_list_wrap(context):
        user = context['request'].user
        farm_list = Farm.objects.filter( Q(farmer=user) |
                                         Q(users=user) ).distinct()
        context['farm_list'] = farm_list
        return ''

    return ContextNode(farm_list_wrap)


@register.tag
def planting_list(parser, token): 
    """
    Return a list of all Planting objects corresponding to request.user
    """

    print "In planting_list tag"

    def planting_list_wrap(context):
        user = context['request'].user
        planting_list = Planting.objects.filter( Q(field_list__farm__farmer=user) |
                                        Q(field_list__farm__users=user) ).distinct()
        context['planting_list'] = planting_list
        return ''

    return ContextNode(planting_list_wrap)



