from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt

import datetime, re
from dateutil import parser

from farms.models import WaterRegister, CropSeason, Field

import django

    


# @method_decorator(login_required)
def plot_daily_use(request, crop_season, field):

    
    date_str = request.session['today_date']

    # date_str has the form yyyy-mm-dd.
    pattern = re.compile("(\d+)\-(\d+)\-(\d+)")
    m = pattern.match(date_str)

    today_date = datetime.date(int (m.group(1)), int (m.group(2)), int (m.group(3)))
    print 'today_date: ', today_date

    # Get the water register objects 10 days before and 10 days after today's date

    cs = CropSeason.objects.get(pk=crop_season)
    fld = Field.objects.get(pk=field)
    start_date = today_date - datetime.timedelta(days = 10)
    end_date = today_date + datetime.timedelta(days = 10)

    wr_list = WaterRegister.objects.filter(crop_season = cs,
                                           field = fld,
                                           date__lte = end_date,
                                           date__gte = start_date).order_by('date')
    print 'wr records, ordered:'
    for wr in wr_list:
        print wr.date


    fig=Figure()

    wu_plot_before=fig.add_subplot(111)
    ir_plot_before=fig.add_subplot(111)
    rf_plot_before=fig.add_subplot(111)

    wu_plot_after=fig.add_subplot(111)
    ir_plot_after=fig.add_subplot(111)
    rf_plot_after=fig.add_subplot(111)


    

    x=[]
    x_pre = []
    x_post= []

    wu_pre=[]
    rf_pre=[]
    ir_pre=[]

    wu_post=[]
    rf_post=[]
    ir_post=[]
    for wr in wr_list:
        x.append(wr.date)
        if (wr.date <= today_date):
            wu_pre.append(wr.daily_water_use)
            rf_pre.append(wr.rain)
            ir_pre.append(wr.irrigation)
            x_pre.append(wr.date)
        if (wr.date >= today_date):
            wu_post.append(wr.daily_water_use)
            rf_post.append(wr.rain)
            ir_post.append(wr.irrigation)
            x_post.append(wr.date)


    wu_plot_before.plot_date(x_pre, wu_pre, 'b-')
    rf_plot_before.plot_date(x_pre, rf_pre, 'g-')
    ir_plot_before.plot_date(x_pre, ir_pre, 'r-')

    wu_plot_after.plot_date(x_post, wu_post, 'b:')
    rf_plot_after.plot_date(x_post, rf_post, 'g-')
    ir_plot_after.plot_date(x_post, ir_post, 'r-')

    wu_plot_before.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    wu_plot_after.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))


    fig.autofmt_xdate()
    fig.suptitle("Daily Water Use", fontsize = 16)
    canvas=FigureCanvas(fig)
    response=django.http.HttpResponse(content_type='image/png')
    canvas.print_png(response)

    return response


def plot_cumulative_use(request, crop_season, field):


    # date_str has the form yyyy-mm-dd.

    date_str = request.session['today_date']
    pattern = re.compile("(\d+)\-(\d+)\-(\d+)")
    m = pattern.match(date_str)

    today_date = datetime.date(int (m.group(1)), int (m.group(2)), int (m.group(3)))
    print 'today_date: ', today_date

    # Get the water register objects 10 days before and 10 days after today's date

    cs = CropSeason.objects.get(pk=crop_season)
    fld = Field.objects.get(pk=field)
    start_date = today_date - datetime.timedelta(days = 10)
    end_date = today_date + datetime.timedelta(days = 10)

    wr_list = WaterRegister.objects.filter(crop_season = cs,
                                           field = fld,
                                           date__lte = end_date,
                                           date__gte = start_date).order_by('date')
    print 'wr records, ordered:'
    for wr in wr_list:
        print wr.date


    fig=Figure()

    wu_plot_before=fig.add_subplot(111)
    ir_plot_before=fig.add_subplot(111)
    rf_plot_before=fig.add_subplot(111)

    wu_plot_after=fig.add_subplot(111)
    ir_plot_after=fig.add_subplot(111)
    rf_plot_after=fig.add_subplot(111)

    x=[]
    x_pre = []
    x_post= []

    wu_pre=[]
    rf_pre=[]
    ir_pre=[]

    wu_post=[]
    rf_post=[]
    ir_post=[]

    cumul_wu = 0
    cumul_rf = 0
    cumul_ir = 0
    for wr in wr_list:
        x.append(wr.date)
        if (wr.date <= today_date):
            wu_pre.append(wr.daily_water_use)
            rf_pre.append(wr.rain)
            ir_pre.append(wr.irrigation)
            x_pre.append(wr.date)
        if (wr.date >= today_date):
            wu_post.append(wr.daily_water_use)
            rf_post.append(wr.rain)
            ir_post.append(wr.irrigation)
            x_post.append(wr.date)


    wu_plot_before.plot_date(x_pre, wu_pre, 'b-')
    rf_plot_before.plot_date(x_pre, rf_pre, 'g-')
    ir_plot_before.plot_date(x_pre, ir_pre, 'r-')

    wu_plot_after.plot_date(x_post, wu_post, 'b:')
    rf_plot_after.plot_date(x_post, rf_post, 'g-')
    ir_plot_after.plot_date(x_post, ir_post, 'r-')

    wu_plot_before.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    wu_plot_after.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))


    fig.autofmt_xdate()
    fig.suptitle("Cumulative Water Use", fontsize = 16)
    canvas=FigureCanvas(fig)
    response=django.http.HttpResponse(content_type='image/png')
    canvas.print_png(response)

    return response




    
