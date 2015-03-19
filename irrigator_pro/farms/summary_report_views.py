from django.shortcuts import get_object_or_404, redirect, render, render_to_response

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView

from django.views.generic.edit import  DeleteView, UpdateView
from django.views.generic import TemplateView

from datetime import date, datetime

from generate_daily_report import generate_daily_report

class SummaryReportListView(TemplateView):
    template_name = "farms/summary_report.html"

    def get(self, request, *args, **kwargs):
        the_date = request.GET.get('date')
        if the_date is not None:
            print 'We have a date: ', the_date
            self.report_date = datetime.strptime(the_date, "%Y-%m-%d").date()
        else:
            self.report_date = date.today()

        return render(request, self.template_name, self.get_context_data())



    #####################################################
    ## Method to gather data and create the query set. ##
    ## Get information for all the farms this user has ##
    ## access to, and only return info for active      ##
    ## fields on these farms.                          ##
    #####################################################

    def get_object_list(self):
        ret_list = generate_daily_report(self.report_date, self.request.user)
        return ret_list


    def get_context_data(self, **kwargs):
        context = super(SummaryReportListView, self).get_context_data(**kwargs)
        context['report_date'] = self.report_date
        context['object_list'] = self.get_object_list()
        return context


    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SummaryReportListView, self).dispatch(*args, **kwargs)
