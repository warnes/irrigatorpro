from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.views import serve
from django.contrib import admin

from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView

from home.views import HomeView
from farms.views import *
from notifications.views import *
from contact_info.views import *
import farms.models

admin.autodiscover()

urlpatterns = patterns('',
                       ## Home Page
                       url(r'^$', HomeView.as_view(), name='home'),

                       ## Static
                       url(r'^%s(?P<path>.*)$' % settings.STATIC_URL.lstrip('/'), serve, {'show_indexes': True, 'insecure': False}),

                       # Enable admin documentation:
                       url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Enable 'smuggler' to provide admin dump/load data support
                       url(r'^admin/', include('smuggler.urls')),

                       ## Uncomment these to enable the admin interface:
                       url(r'^admin_tools/', include('admin_tools.urls')),
                       url(r'^admin/',       include(admin.site.urls)),

                       ## Hijack allows admin users to login as an arbitrary user
                       url(r'^hijack/', include('hijack.urls')),

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
                       url(r'^water_history/$',                               EmptyView.as_view(),                name='water_history'),
                       url(r'^water_history/(?P<season>\d+)$',                EmptyView.as_view(),                name='water_history_season'),
                       url(r'^water_history/(?P<season>\d+)/(?P<field>\d+)$', WaterHistoryFormsetView.as_view(),  name='water_history_season_field'),
                       

                       ## Probe Reading pages
                       url(r'^probe_readings/$',                               EmptyView.as_view(),               name='probe_readings' ),
                       url(r'^probe_readings/(?P<season>\d+)$',                EmptyView.as_view(),               name='probe_reading_season' ),
                       url(r'^probe_readings/(?P<season>\d+)/(?P<field>\d+)$', ProbeReadingFormsetView.as_view(), name='probe_reading_season_field' ),

                       ## Water Register
                       url(r'^water_register/$',                               EmptyView.as_view(),              name='water_register'),
                       url(r'^water_register/(?P<season>\d+)$',                EmptyView.as_view(),              name='water_register_season'),
                       url(r'^water_register/(?P<season>\d+)/(?P<field>\d+)$', WaterRegisterListView.as_view(),  name='water_register_season_field'),
                       url(r'^water_register/(?P<season>\d+)/(?P<field>\d+)/(?P<date>\d{4}-\d{2}-\d{2})$',
                                                                               WaterRegisterListView.as_view(),  name='water_register_season_field_date'),

                       url(r'^water_register/plot/daily/(?P<crop_season>\d+)/(?P<field>\d+)',      
                                                                               'farms.water_register_plots.plot_daily_use',      name='daily_use'),
                       url(r'^water_register/plot/cumulative/(?P<crop_season>\d+)/(?P<field>\d+)',
                                                                               'farms.water_register_plots.plot_cumulative_use', name='cumulative_use'),
                       url(r'^water_register/plot/temperature/(?P<crop_season>\d+)/(?P<field>\d+)',
                                                                               'farms.water_register_plots.plot_daily_temperature', name='daily_temperature'),



                       ## Unified data entry and register. Will eventually replace water register and water history
                       ## but keep everything while testing

                       ## Unified water
                       url(r'^unified_water/$',                               EmptyView.as_view(),                 name='unified_water'),
                       url(r'^unified_water/(?P<season>\d+)$',                EmptyView.as_view(), name='          unified_water_season'),
                       url(r'^unified_water/(?P<season>\d+)/(?P<field>\d+)$', UnifiedFieldDataListView.as_view(),  name='unified_water_season_field'),
                       url(r'^unified_water/(?P<season>\d+)/(?P<field>\d+)/(?P<date>\d{4}-\d{2}-\d{2})$',
                                                                              UnifiedFieldDataListView.as_view(),  name='unified_water_season_field_date'),


                       ## Reports 
                       url(r'^report/$',                                        HomeView.as_view(),              name='report'),
                       url(r'^report/summary_report/$',                         SummaryReportListView.as_view(), name='summary_report'),
                       url(r'^report/summary_report/(?P<date>\d{4}-\d{2}-\d{2})$',
                                                                                SummaryReportListView.as_view(), name='summary_report_date'),

                       url(r'^report/cumulative_report/$',                      CumulativeReportView.as_view(),  name='cumulative_report'),
                       url(r'^report/cumulative_report/(?P<start_date>\d{4}-\d{2}-\d{2})/(?P<end_date>\d{4}-\d{2}-\d{2})$',
                                                                                CumulativeReportView.as_view(),  name='cumulative_report'),

                       ## Notification pages

                       url(r'^settings/notifications/$',                        NotificationsSetupView.as_view(), name="notifications"),


                       ## User pages
                       #url(r'^user/edit$',  edit_user  ),
                       url(r'^settings/user_name/$',    UserUpdateView.as_view(),         name='user_name'  ),
                       url(r'^settings/contact_info/$', Contact_InfoUpdateView.as_view(), name='contact_info'  ),
                       url(r'^settings/validate_sms/$', 'contact_info.views.validate_sms',  name='validate_sms'),
                       url(r'^sms-incoming',    'contact_info.views.incoming_sms', name='sms-incoming'),

                       ## Ajax pages for available users for contact info.
                       ## Two separate links because a farm may not exists at the time this is invoked.
                       url(r'^filter_auth/$',                    'contact_info.views.get_available_users', name='filter_auth_users'),
                       url(r'^filter_auth/(?P<farm_pk>\d+)/',    'contact_info.views.get_available_users', name='filter_auth_users_farm'),

                       ## Ajax pages for notifications.

                       ## Fields assigned to a crop season
                       url(r'^notification_fields/',
                           'notifications.notifications_setup_view.get_fields_list',
                           name='notification_fields'),

                       ## Users assigned to a farm
                       url(r'^notification_users/(?P<farm_pk>\d+)/', 
                           'notifications.notifications_setup_view.get_users_list',
                           name='notification_users'),

)






if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
