# View for cumulative report

from django.shortcuts import get_object_or_404, redirect, render, render_to_response
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from datetime import date, datetime

from django.views.generic import TemplateView

from generate_cumulative_report import generate_cumulative_report

class CumulativeReportView(TemplateView):
    template_name = "farms/cumulative_report_list.html"
    
    def get(self, request, *args, **kwargs):
        
        requested_start_date = request.GET.get('start_date')
        requested_end_date = request.GET.get('end_date')

        if requested_start_date is None:
            self.end_date = date.today()
            self.start_date = date(self.end_date.year, 1, 1)
        else:
            self.start_date = datetime.strptime(requested_start_date, "%Y-%m-%d").date()
            self.end_date = datetime.strptime(requested_end_date, "%Y-%m-%d").date()

        return render(request, self.template_name, self.get_context_data())
            


    def get_object_list(self):
        ret_list = generate_cumulative_report(self.start_date, self.end_date, self.request.user)
        return ret_list


    def get_context_data(self, **kwargs):
        context = super(CumulativeReportView, self).get_context_data(**kwargs)
        context['start_date'] = self.start_date
        context['end_date'] = self.end_date
        context['today_date'] = date.today()
        context['earliest_date'] = date(2013,1,1)
        context['object_list'] = self.get_object_list()
        return context


    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CumulativeReportView, self).dispatch(*args, **kwargs)

