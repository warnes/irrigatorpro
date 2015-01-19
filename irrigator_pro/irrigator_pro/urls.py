from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.views import serve
from django.contrib import admin

from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView

from home.views import HomeView
from farms.views import *
from contact_info.views import *
import farms.models

admin.autodiscover()

urlpatterns = patterns('',
                       ## Home Page
                       url(r'^$', HomeView.as_view(), name='home'),

                       ## Static
                       url(r'^%s(?P<path>.*)$' % settings.STATIC_URL.lstrip('/'), serve, {'show_indexes': True, 'insecure': False}),

                       # Uncomment the admin/doc line below to enable
                       # admin documentation:
                       url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       ## Uncomment these to enable the admin interface:
                       url(r'^admin_tools/', include('admin_tools.urls')),
                       url(r'^admin/',       include(admin.site.urls)),

                       ######################
                       ## User Authentication 
                       ######################

                       ## User authentication via django-allauth
                       (r'^accounts/', include('allauth.urls')),

                       ## Session Timeout
                       url(r'session_security/', include('session_security.urls')),

                       ###########
                       ## Settings 
                       ###########

                       ## Top level target
                       url(r'^settings/$', HomeView.as_view(), name='settings'),

                       ## Farm pages
                       url(r'^settings/farm/$',                   FarmListView.as_view(),   name='farm_list'),
                       url(r'^settings/farm/new$',                FarmCreateView.as_view(), name='farm_new'),
                       url(r'^settings/farm/delete/(?P<pk>\d+)$', FarmDeleteView.as_view(), name='farm_delete'),
                       url(r'^settings/farm/(?P<pk>\d+)$',        FarmUpdateView.as_view(), name='farm_id'),

                       ## Probe pages
                       url(r'^settings/probes/$',                 ProbeFormsetView.as_view(), name='probes' ),
                       url(r'^settings/probes/(?P<season>\d+)$',  ProbeFormsetView.as_view(), name='probes_season' ),

                       # ## CropSeason pages
                       url(r'^settings/crop_season/$',                   CropSeasonListView.as_view(),   name='crop_season_list'),
                       url(r'^settings/crop_season/new$',                CropSeasonCreateView.as_view(), name='crop_season_new'),
                       url(r'^settings/crop_season/delete/(?P<pk>\d+)$', CropSeasonDeleteView.as_view(), name='crop_season_delete'),
                       url(r'^settings/crop_season/(?P<pk>\d+)$',        CropSeasonUpdateView.as_view(), name='crop_season_id'),

                       #############
                       ## Main Pages
                       #############

                       ## Water History
                       url(r'^water_history/$',                               WaterHistoryFormsetView.as_view(),   name='water_history'),
                       url(r'^water_history/(?P<season>\d+)$',                WaterHistoryFormsetView.as_view(),   name='water_history_season'),
                       url(r'^water_history/(?P<season>\d+)/(?P<field>\d+)$', WaterHistoryFormsetView.as_view(),   name='water_history_season_field'),
                       

                       ## Probe Reading pagesw
                       url(r'^probe_readings/$',                               ProbeReadingFormsetView.as_view(), name='probe_readings' ),
                       url(r'^probe_readings/(?P<season>\d+)$',                ProbeReadingFormsetView.as_view(), name='probe_reading_season' ),
                       url(r'^probe_readings/(?P<season>\d+)/(?P<field>\d+)$', ProbeReadingFormsetView.as_view(), name='probe_reading_season_field' ),

                       ## Water Register
                       url(r'^water_register/$',                               HomeView.as_view(),              name='water_register'),
                       url(r'^water_register/(?P<season>\d+)$',                WaterRegisterListView.as_view(), name='water_register_season'),
                       url(r'^water_register/(?P<season>\d+)/(?P<field>\d+)$', WaterRegisterListView.as_view(), name='water_register_season_field'),
                       url(r'^water_register/plot/daily/temp.png', 'farms.water_register_plots.plot_daily_use', name='daily_use'),

                       ## Summary report
                       url(r'^summary_report/$',                               SummaryReportListView.as_view(),   name='summary_report'),
                       url(r'^summary_report/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)$',  SummaryReportListView.as_view(),   name='summary_report'),

                       ## User pages
                       #url(r'^user/edit$',  edit_user  ),
                       url(r'^user/user_name/$',    UserUpdateView.as_view(),         name='user_name'  ),
                       url(r'^user/contact_info/$', Contact_InfoUpdateView.as_view(), name='contact_info'  ),

)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
