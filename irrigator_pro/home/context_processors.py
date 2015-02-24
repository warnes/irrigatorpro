from irrigator_pro import settings

def sitevars(request):
    "A context processor that provides seletected site-wide settings"
    vars = {
        'site_name': settings.SITE_NAME,
           }
    return vars

def global_settings(request):
    return {
        'GA_KEY': settings.GA_KEY
    } 
