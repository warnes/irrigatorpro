#! /usr/bin/env python2.7
from default import *

"""
This is the local settings file. 
"""

# local settings
DEBUG = True
TEMPLATE_DEBUG = DEBUG

SITE_NAME = "IrrigatorPro (Devel)"

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'XXXXXX',
        'USER': 'XXXXXX',
        'PASSWORD': 'XXXXXXX',
        'HOST': 'localhost',
        'PORT': '',
        },
    'ugatifton': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'ugatifton',
        'USER': 'XXXXXX',
        'PASSWORD': 'XXXXX',
        'HOST': 'XXXXX',
        'PORT': '',
        },
}

##
# For testing, don't use UGA database
##
TEST_RUNNING = 'test' in sys.argv
if TEST_RUNNING:
    DATABASE_ROUTERS = []
    DATABASES.pop('ugatifton')

###
# Google Analytics
###
GA_KEY = "XXXXX"


###
# Security Settings
###

# Make this unique, and don't share it with anybody.
# http://www.miniwebtool.com/django-secret-key-generator/
SECRET_KEY="XXXXX"

ALLOWED_HOSTS = [ 'XXXXX' ]

### 
# URL for Notification link back to server
###
NOTIFICATION_HOST = "http://XXXXX/farm/report/summary_report/"



### 
# Debugging settings
###

if DEBUG:
    # set INTERNAL_IPS to entire local network
    from fnmatch import fnmatch

    class WildcardNetwork(list):
        def __contains__(self, key):
            for address in self:
                if fnmatch(key, address):
                    return True
            return False

    INTERNAL_IPS = WildcardNetwork(['*'])

    INSTALLED_APPS += (
        'debug_toolbar',
    )

    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

    # django-debug-toolbar specific
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ]

    DEBUG_TOOLBAR_PATCH_SETTINGS = False

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
        # 'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar_function,
        #'EXTRA_SIGNALS': ['myproject.signals.MySignal'],
        'INSERT_BEFORE': '</body>',
    }

    #EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    ###
    # django-session-security Session Timeout Settings
    ###

    # WARN_AFTER
    #    Time (in seconds) before the user should be warned that is session will 
    #    expire because of inactivity. Default 540. 
    SESSION_SECURITY_WARN_AFTER=60 * 60 * 11 # 11 hours

    # EXPIRE_AFTER
    #    Time (in seconds) before the user should be logged out if inactive. Default
    #    is 600. 
    SESSION_SECURITY_EXPIRE_AFTER=60 * 60 * 12 # 12 hours
    
    # PASSIVE_URLS
    #    List of urls that should be ignored by the middleware. For example the 
    #    ping ajax request of session_security is made without user intervention,
    #    as such it should not be used to update the user's last activity datetime.
    # SESSION_SECURITY_PASSIVE_URLS=[]

    # EXPIRE_AT_BROWSER_CLOSE
    #    Required for this module to operate properl
    SESSION_EXPIRE_AT_BROWSER_CLOSE=False

