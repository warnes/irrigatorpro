from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.views import serve
from django.contrib import admin
from home.views import HomeView

admin.autodiscover()

urlpatterns = patterns('',
                       ## Home Page
                       url(r'^$', HomeView.as_view(), name='home'),
                       
                       ## Static
                       url(r'^%s(?P<path>.*)$' % settings.STATIC_URL.lstrip('/'), serve, {'show_indexes': True, 'insecure': False}),
                       
                       ## Admin interface
                       url(r'^admin/password_reset/$', 'django.contrib.auth.views.password_reset', name='admin_password_reset'),

                       url(r'^admin/password_reset/done/$', 'django.contrib.auth.views.password_reset_done', name='password_reset_done'),

                       url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', name='password_reset_confirm'),  

                       url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete', name='password_reset_complete'), 

                       # Uncomment the admin/doc line below to enable
                       # admin documentation: 
                       url(r'^admin/doc/', include('django.contrib.admindocs.urls')), 

                       # Uncomment these to enable the admin interface: 
                       url(r'^admin_tools/', include('admin_tools.urls')),
                       url(r'^admin/', include(admin.site.urls)),

                       ## User authorization
                       url(r'^accounts/login/$',  'django.contrib.auth.views.login'),
                       url(r'^accounts/logout/$', 'django.contrib.auth.views.login'),

)

