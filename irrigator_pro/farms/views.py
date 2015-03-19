""" Load actual views from model-specific files"""
from farm_views import *
from crop_season_views import *
from formset_views import ProbeFormsetView, WaterHistoryFormsetView
from probe_reading_views import ProbeReadingFormsetView
from water_register_views import WaterRegisterListView
from summary_report_views import SummaryReportListView
from cumulative_report_view import CumulativeReportView
from water_register_plots import *

