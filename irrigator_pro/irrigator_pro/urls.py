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

                       # ## Admin interface
                       # url(r'^admin/password_reset/$',                            'django.contrib.auth.views.password_reset',          name='admin_password_reset'),
                       # url(r'^admin/password_reset/done/$',                       'django.contrib.auth.views.password_reset_done',     name='password_reset_done'),
                       # url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm',  name='password_reset_confirm'),
                       # url(r'^reset/done/$',                                      'django.contrib.auth.views.password_reset_complete', name='password_reset_complete'),

                       # Uncomment the admin/doc line below to enable
                       # admin documentation:
                       url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       ## Uncomment these to enable the admin interface:
                       url(r'^admin_tools/', include('admin_tools.urls')),
                       url(r'^admin/',       include(admin.site.urls)),

                       ## User authentication via django-allauth
                       (r'^accounts/', include('allauth.urls')),
                       url(r'^accounts/contact_info/$',  Contact_InfoUpdateView.as_view(), name='contact_info'  ),

                       ## Session Timeout
                       url(r'session_security/', include('session_security.urls')),

                       ## Farm pages
                       # url(r'^farm/$',  ListView.as_view(
                       #                      model=farms.models.Farm,
                       #                      template_name="list.html",
                       #                      ),
                       #                   name='farm_list_view'
                       # ),
                       url(r'^farm/$',                   FarmListView.as_view(),   name='farm_list'),
                       url(r'^farm/new$',                FarmCreateView.as_view(), name='farm_new'),
                       url(r'^farm/delete/(?P<pk>\d+)$', FarmDeleteView.as_view(), name='farm_delete'),
                       url(r'^farm/(?P<pk>\d+)$',        FarmUpdateView.as_view(), name='farm_id'),

                       ## Probe pages
                       url(r'^probes/$',                 ProbeFormsetView.as_view(), name='probes' ),
                       url(r'^probes/(?P<season>\d+)$',  ProbeFormsetView.as_view(), name='probes_season' ),


                       # ## CropSeason pages
                       url(r'^crop_season/$',                   CropSeasonListView.as_view(),   name='crop_season_list'),
                       url(r'^crop_season/new$',                CropSeasonCreateView.as_view(), name='crop_season_new'),
                       url(r'^crop_season/delete/(?P<pk>\d+)$', CropSeasonDeleteView.as_view(), name='crop_season_delete'),
                       url(r'^crop_season/(?P<pk>\d+)$',        CropSeasonUpdateView.as_view(), name='crop_season_id'),

                       ## Water History
                       url(r'^water_history/$',                               WaterHistoryFormsetView.as_view(),   name='water_history'),
                       url(r'^water_history/(?P<season>\d+)$',                WaterHistoryFormsetView.as_view(),   name='water_history_season'),
                       url(r'^water_history/(?P<season>\d+)/(?P<field>\d+)$', WaterHistoryFormsetView.as_view(),   name='water_history_season_field'),

                       ## Probe Reading pages
                       url(r'^probe_readings/$',                               ProbeReadingFormsetView.as_view(), name='probe_readings' ),
                       url(r'^probe_readings/(?P<season>\d+)$',                ProbeReadingFormsetView.as_view(), name='probe_reading_season' ),
                       url(r'^probe_readings/(?P<season>\d+)/(?P<field>\d+)$', ProbeReadingFormsetView.as_view(), name='probe_reading_season_field' ),

                       ## Water Register
                       url(r'^water_register/$',                               HomeView.as_view(), name='water_register'),
                       url(r'^water_register/(?P<season>\d+)$',                HomeView.as_view(), name='water_register_season'),
                       url(r'^water_register/(?P<season>\d+)/(?P<field>\d+)$', HomeView.as_view(), name='water_register_season_field'),

                       ## User pages
                       #url(r'^user/edit$',  edit_user  ),
                       url(r'^user/$', HomeView.as_view(), name="user"  ),
                       url(r'^user/(?P<userid>\w+)$', UserDetailView.as_view()  ),


)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
