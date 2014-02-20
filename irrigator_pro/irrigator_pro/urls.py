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
from recipe.views import *

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
 
                       ## Session Timeout
                       url(r'session_security/', include('session_security.urls')),

                       ## User pages
                       url(r'^contact_info/$',  Contact_InfoUpdateView.as_view()  ),

                       ## Farm pages
                       # url(r'^farm/$',  ListView.as_view(
                       #                      model=farms.models.Farm,
                       #                      template_name="list.html",
                       #                      ),
                       #                   name='farm_list_view'
                       # ),
                       url(r'^farm/$',                   FarmListView.as_view()   ),
                       url(r'^farm/new$',                FarmCreateView.as_view() ),
                       url(r'^farm/delete/(?P<pk>\w+)$', FarmDeleteView.as_view() ),
                       url(r'^farm/(?P<pk>\w+)$',        FarmUpdateView.as_view() ),

                       

                       ## Field pages
                       url(r'^field/$',  ListView.as_view(
                                            model=farms.models.Field,
                                            template_name="list.html",
                                            ),
                                         name='field_list_view'
                       ),


                       ## User pages
                       #url(r'^user/edit$',  edit_user  ),
                       #url(r'^user/$', UserDetailView.as_view()  ),
                       #url(r'^user/(?P<userid>\w+)$', UserDetailView.as_view()  ),

                       ## Demo recipe pages
                       url(r'^recipe/add$', RecipeCreateView.as_view() )



)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
