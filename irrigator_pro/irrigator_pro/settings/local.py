#! /usr/bin/env python2.7
from default import *

"""
This is the local settings template file. So, do not modify this file.
Instead, make a copy as "local.py" and set the development variables in it.
"""

# local settings
DEBUG = True
TEMPLATE_DEBUG = DEBUG


# DATABASES = {
#     'default': {
#         # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#         # The rest is not used with sqlite3:
#         'USER': 'dev_user',
#         'PASSWORD': 'dev_p@ssword',
#         'HOST': 'localhost',
#         'PORT': '',
#     }
# }


if DEBUG:
    # set INTERNAL_IPS to entire local network
    from fnmatch import fnmatch

    class WildcardNetwork(list):
        def __contains__(self, key):
            for address in self:
                if fnmatch(key, address):
                    return True
            return False

    INTERNAL_IPS = WildcardNetwork(['127.0.0.1', '192.168.*.*'])

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

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
        # 'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar_function,
        #'EXTRA_SIGNALS': ['myproject.signals.MySignal'],
        'INSERT_BEFORE': 'div',
    }
