#! /usr/bin/env python2.7
from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = 'home.html'

#    def get(self, request, *args, **kwargs):
#        context = {
#            'some_dynamic_value': 'Current Status: Validation',
#        }
#        return self.render_to_response(context)
