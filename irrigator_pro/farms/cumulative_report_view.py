# View for cumulative report

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from datetime import date, datetime


from django.views.generic import TemplateView



class CumulativeReportView(TemplateView):
    template_name = "farms/cumulative_report.html"
    
    def get(self, request, *args, **kwargs):
        
        startDate = request.GET.get('start_date')
        endDate = requset.GET.get('end_date')

        if startDate 





class CumulativeReportFields:
    farm                        = 'Unknown farm'
    field                       = 'Unknown field'
    crop                        = 'Unknown crop'
    season_start_date           = 'No Entry'
    season_end_date             = "No Entry"
    cumulative_water_use        = 0.0
    cumulative_rain             = 0.0
    cumulative_irrigation       = 0.0
    nb_irrigation_days          = 0.0
    
    
    