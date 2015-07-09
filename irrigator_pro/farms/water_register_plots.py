from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
from decimal import Decimal

import datetime, re
from dateutil import parser

from farms.models import WaterRegister, CropSeason, Field

import django

# workarounds for the absence of query datetime__date operator
from common.utils import d2dt_min, d2dt_max, d2dt_range

import matplotlib as mp
# Set default font size
mp.rcParams['axes.titlesize'] = "x-large" # fontsize of the axes title
mp.rcParams['axes.labelsize'] = "large"   # fontsize of the x any y labels

# Set default line widths
mp.rcParams['axes.linewidth' ] = 2
mp.rcParams['lines.linewidth'] = 2
mp.rcParams['patch.linewidth'] = 2

def get_report_date(date_str):
    # date_str has the form yyyy-mm-dd.
    pattern = re.compile("(\d+)\-(\d+)\-(\d+)")
    m = pattern.match(date_str)

    report_date = datetime.date(int (m.group(1)), int (m.group(2)), int (m.group(3)))
    print 'report_date: ', report_date
    return report_date


def get_water_register_list(report_date, crop_season, field):

    # Different formulas whether today is during or after crop season:
    # Within crop season: everything till today plus 10 days
    # After crop season: everything

    cs = CropSeason.objects.get(pk=crop_season)
    fld = Field.objects.get(pk=field)
    start_date = cs.season_start_date
    end_date = min(report_date + datetime.timedelta(days = 10),
                   cs.season_end_date)

    wr_list = WaterRegister.objects.filter(crop_season = cs,
                                           field = fld,
                                           datetime__lte = d2dt_min(end_date),
                                           datetime__gte = d2dt_max(start_date)
                                           ).order_by('datetime')
    return wr_list
    

def plot_daily_use(request, crop_season, field):

    report_date = get_report_date(request.session['report_date'])
    wr_list = get_water_register_list(report_date, crop_season, field)

    fig=Figure()

    wu_plot_before=fig.add_subplot(111)
    ir_plot_before=fig.add_subplot(111)
    rf_plot_before=fig.add_subplot(111)
    aw_plot_before=fig.add_subplot(111)

    wu_plot_after=fig.add_subplot(111)
    ir_plot_after=fig.add_subplot(111)
    rf_plot_after=fig.add_subplot(111)
    aw_plot_after=fig.add_subplot(111)
    
    x=[]
    x_before = []
    x_after= []

    wu_before=[]
    rf_before=[]
    ir_before=[]
    aw_before=[]

    wu_after=[]
    rf_after=[]
    ir_after=[]
    aw_after=[]
    for wr in wr_list:
        x.append(wr.datetime.date())

        # NB: entries on report_date need to be in both groups to make
        # line continuous
        if (wr.datetime.date() <= report_date):
            wu_before.append(wr.daily_water_use)
            rf_before.append(wr.rain)
            ir_before.append(wr.irrigation)
            aw_before.append(wr.average_water_content)
            x_before.append(wr.datetime.date())

        if (wr.datetime.date() >= report_date):
            wu_after.append(wr.daily_water_use)
            rf_after.append(wr.rain)
            ir_after.append(wr.irrigation)
            aw_after.append(wr.average_water_content)
            x_after.append(wr.datetime.date())

    wu_plot_before.plot_date(x_before, wu_before, 'g-', label = "Water Usage")
    rf_plot_before.plot_date(x_before, rf_before, 'c-', label = "Rain",                  drawstyle='steps-pre')
    ir_plot_before.plot_date(x_before, ir_before, 'b-', label = "Irrigation",            drawstyle='steps-pre')
    aw_plot_before.plot_date(x_before, aw_before, 'r-', label = "Average Water Content")

    #rf_plot_before.vlines(x=x_before, ymin=0, ymax=rf_before, colors='c', linestyles='solid', label = "Rain")
    #ir_plot_before.vlines(x=x_before, ymin=0, ymax=ir_before, colors='b', linestyles='solid', label = "Irrigation")


    wu_plot_after.plot_date(x_after, wu_after, 'g:')
    #rf_plot_after.plot_date(x_after, rf_after, 'c:', drawstyle='steps-pre')
    #ir_plot_after.plot_date(x_after, ir_after, 'b:', drawstyle='steps-pre')
    aw_plot_after.plot_date(x_after, aw_after, 'r:')

    #rf_plot_after.vlines(x=x_after, ymin=0, ymax=rf_after, colors='c', linestyles='dotted')
    #ir_plot_after.vlines(x=x_after, ymin=0, ymax=ir_after, colors='b', linestyles='dotted')


    wu_plot_before.legend(loc = 'best')
    wu_plot_before.set_ylabel("Inches", fontsize=16)

    wu_plot_before.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    wu_plot_after.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))

    wu_plot_before.grid()

    fig.autofmt_xdate()
    fig.suptitle("Daily Water", fontsize = 20)
    canvas=FigureCanvas(fig)
    response=django.http.HttpResponse(content_type='image/png')
    fig.savefig(response, transparent=True, format='png')

    return response


def plot_cumulative_use(request, crop_season, field):

    report_date = get_report_date(request.session['report_date'])
    wr_list = get_water_register_list(report_date, crop_season, field)

    fig=Figure()

    wu_before_plot=fig.add_subplot(111)
    ir_before_plot=fig.add_subplot(111)
    rf_before_plot=fig.add_subplot(111)
    tw_before_plot=fig.add_subplot(111) # tw=total water = ir+rf

    wu_after_plot=fig.add_subplot(111)
    ir_after_plot=fig.add_subplot(111)
    rf_after_plot=fig.add_subplot(111)
    tw_after_plot=fig.add_subplot(111) # tw=total water = ir+rf

    x_before=[]
    wu_before=[]
    rf_before=[]
    ir_before=[]
    tw_before=[]

    x_after=[]
    wu_after=[]
    rf_after=[]
    ir_after=[]
    tw_after=[]

    wu_total = 0
    ir_total = 0
    rf_total = 0
    tw_total = 0
    for wr in wr_list:
        wu_total += wr.daily_water_use
        rf_total += wr.rain
        ir_total += wr.irrigation
	tw_total += wr.rain + wr.irrigation

        # NB: entries on report_date need to be in both groups to make
        # line continuous
        if (wr.datetime.date() <= report_date):
            x_before.append(wr.datetime.date())
            wu_before.append(wu_total)

            #NB: offset these slightly so they are all visible even when rf and/or ir are zero 
            rf_before.append(rf_total)
            ir_before.append(ir_total + Decimal(0.1) )               
            tw_before.append(tw_total + Decimal(0.2) )

        if (wr.datetime.date() >= report_date):
            x_after.append(wr.datetime.date())
            wu_after.append(wu_total)

            #NB: offset these slightly so they are all visible even when rf and/or ir are zero 
            rf_after.append(rf_total)
            ir_after.append(ir_total + Decimal(0.1) )
            tw_after.append(tw_total + Decimal(0.2) )

    wu_before_plot.plot_date(x_before, wu_before, 'g-', label = "Water Usage")
    rf_before_plot.plot_date(x_before, rf_before, 'c-', label = "Rain")
    ir_before_plot.plot_date(x_before, ir_before, 'b-', label = "Irrigation")
    tw_before_plot.plot_date(x_before, tw_before, 'm-', label = "Rain + Irrigation")

    wu_after_plot.plot_date(x_after, wu_after, 'g:')
    rf_after_plot.plot_date(x_after, rf_after, 'c:')
    ir_after_plot.plot_date(x_after, ir_after, 'b:')
    tw_after_plot.plot_date(x_after, tw_after, 'm:')

    wu_before_plot.legend(loc = 'best')

    wu_before_plot.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    wu_before_plot.set_ylabel("Inches", fontsize=16)

    wu_before_plot.grid()

    fig.autofmt_xdate()
    canvas=FigureCanvas(fig)
    fig.suptitle("Cumulative Water", fontsize = 20)
    response=django.http.HttpResponse(content_type='image/png')
    fig.savefig(response, transparent=True, format='png')

    return response




    
