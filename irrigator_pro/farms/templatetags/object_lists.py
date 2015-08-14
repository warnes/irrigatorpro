from django.db.models import Q
from django.template import Library, Node, TemplateSyntaxError, resolve_variable
from farms.models import Farm, CropSeason
from operator import itemgetter, attrgetter, methodcaller
from sys import stdout, stderr


register = Library()

class ContextNode(Node):
  def __init__(self, func):
    self.func = func

  def render(self, context):
    return self.func(context)

@register.tag
def farm_list(parser, token):
    """
    Return a list of all Farm objects corresponding to request.user
    """
    def farm_list_wrap(context):
        if 'farm_list' in context: return ''  # use existing result if present

        user = context['request'].user
        farm_list = Farm.objects.filter( Q(farmer=user) |
                                         Q(users=user) ).distinct().prefetch_related('field_set')
        context['farm_list'] = farm_list

        for farm in farm_list:
            farm.field_list = farm.field_set.get_queryset()

        return ''

    return ContextNode(farm_list_wrap)


@register.tag
def crop_season_list(parser, token):
    """
    Return a list of all CropSeason objects corresponding to request.user
    """
    def crop_season_list_wrap(context):
        if 'crop_season_list' in context: return ''  # use existing result if present

        user = context['request'].user
        crop_season_list = CropSeason.objects.filter( Q(field_list__farm__farmer=user) |
                                                      Q(field_list__farm__users=user) ).\
                                  distinct().order_by('name'). \
                                  prefetch_related('field_list', 
                                                   'field_list__farm',
                                                   'probe_set', 
                                                   #'probe_set__field'
                                                   )
        context['crop_season_list'] = crop_season_list
        
        for crop_season in crop_season_list:
            crop_season.year           = crop_season.season_start_date.year
            crop_season.field_list_all = crop_season.field_list.all()
            crop_season.probe_list_all = crop_season.probe_set.all() \
                                                     .select_related('field')  \
                                                     .distinct() 

            probe_field_list = []
            for probe in crop_season.probe_list_all:
              probe_field_list.append( (probe.field, probe) )

            #probe_field_list.sort(key=lambda i:str(i[0]) )
            crop_season.probe_field_list = probe_field_list

        return ''

    return ContextNode(crop_season_list_wrap)





