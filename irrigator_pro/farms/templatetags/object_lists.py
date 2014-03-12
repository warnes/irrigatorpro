from sys import stdout, stderr
from farms.models import Farm, CropSeason
from django.db.models import Q
from django.template import Library, Node, TemplateSyntaxError, resolve_variable

register = Library()

class ContextNode(Node):
  def __init__(self, func):
    self.func = func

  def render(self, context):
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
    def farm_list_wrap(context):
        user = context['request'].user
        farm_list = Farm.objects.filter( Q(farmer=user) |
                                         Q(users=user) ).distinct()
        context['farm_list'] = farm_list

        for farm in farm_list:
            farm.field_list = farm.field_set.get_query_set()

        return ''

    return ContextNode(farm_list_wrap)


@register.tag
def crop_season_list(parser, token):
    """
    Return a list of all CropSeason objects corresponding to request.user
    """
    def crop_season_list_wrap(context):
        user = context['request'].user
        crop_season_list = CropSeason.objects.filter( Q(field_list__farm__farmer=user) |
                                                      Q(field_list__farm__users=user) ).distinct()
        context['crop_season_list'] = crop_season_list

        for crop_season in crop_season_list:
            crop_season.field_list_all = crop_season.field_list.all()
            crop_season.probe_list_all = crop_season.probe_set.all()
            probe_field_list = []
            for probe in crop_season.probe_set.all():
                for field in probe.field_list.all():
                    probe_field_list.append( (field, probe) )


            probe_field_list.sort(key=lambda i:str(i[0]) )
            crop_season.probe_field_list = probe_field_list

        return ''

    return ContextNode(crop_season_list_wrap)





