from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

class EmptyView(TemplateView):
    template_name = 'farms/empty.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EmptyView, self).dispatch(*args, **kwargs)
