#! /usr/bin/env python2.7
"""
Django settings for IrrigatorPro Web Site
"""

import os
import re
import sys

###
# Where am I?
###

TEST_RUNNER = 'django.test.runner.DiscoverRunner' 
ABSOLUTE_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..'))

###
# Number of days in future where we generate a water register.
###
WATER_REGISTER_DELTA = 7


###
# Use ConfigParser to pull private values from irrigator_pro.conf
### 

import ConfigParser
config = ConfigParser.ConfigParser()
config.read(os.path.join(ABSOLUTE_PROJECT_ROOT, "irrigator_pro", "settings", "irrigator_pro.conf"))
def unquote(str):
    str = re.sub(r'^\"(.*)\"$', '\\1', str)
    str = re.sub(r'^\'(.*)\'$', '\\1', str)
    return str

###
# Site settings
###

# Name displayed on pages, for easy change
SITE_NAME = "IrrigatorPro (Devel)"

# Make this unique, and don't share it with anybody.
# http://www.miniwebtool.com/django-secret-key-generator/
SECRET_KEY = unquote(config.get('Django','SECRET_KEY'))

SITE_ID = 1

ADMINS = (
    ('Gregory R. Warnes', 'greg@warnes.net'       ),
    ('Bill Edwards',      'edwardsb2001@yahoo.com'),
    ('Alain Leblanc',     'aalebl@gmail.com'      ),
    ('Tony Winter',       'tony@warnes.net'       ),
)

MANAGERS = ADMINS

###
# Debug settings
###

DEBUG = True
TEMPLATE_DEBUG = DEBUG

#COMPUTE_FULL_SEASON = True   #  Calculate water register through the end of the season.
COMPUTE_FULL_SEASON = False  # If False, only calculate water register through today + 5 days.



###
# Paths
###

ABSOLUTE_TEMPLATES_PATH = os.path.abspath(os.path.join(ABSOLUTE_PROJECT_ROOT, 'templates/'))

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.abspath(os.path.join(ABSOLUTE_PROJECT_ROOT, 'static/'))
# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = os.path.abspath(os.path.join(ABSOLUTE_PROJECT_ROOT, 'media/'))

# URL that handles the media, static, etc.
STATIC_URL = '/static/'
MEDIA_URL =  '/media/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.abspath(os.path.join(ABSOLUTE_PROJECT_ROOT, 'staticfiles/')),
)

###
# Database settings
###

DATABASES = {
    'default': {
        ## Use sqlite3 for development ##
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(ABSOLUTE_PROJECT_ROOT, 'db.sqlite3'),
	'timeout': 20,
        ##

        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        #'ENGINE': 'django.db.backends.postgresql_psycopg2',
        #'NAME': 'prod_database_name',
        # The rest is not used with sqlite3:
        'USER': 'prod_user',
        'PASSWORD': 'prod_p@ssword',
        'HOST': 'localhost',
        'PORT': '',
    }
}

###
# Localization
###

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'US/Eastern'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

###
# Finders/Loaders
###

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'common.middleware.AuditMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'session_security.middleware.SessionSecurityMiddleware',
)

ROOT_URLCONF = 'irrigator_pro.urls'

# Python dotted path to the WSGI application used by Django's runserver.
# disabled - outsite the app
WSGI_APPLICATION = 'irrigator_pro.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    ABSOLUTE_TEMPLATES_PATH,
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'home.context_processors.sitevars',
    # default template context processors
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    # required by django-admin-tools and django-allauth
    'django.core.context_processors.request',
    #'django.contrib.messages.context_processors.messages',
    'allauth.account.context_processors.account',
    'allauth.socialaccount.context_processors.socialaccount',    
    'home.context_processors.global_settings',
    
)

###
# APPS
###

# django debugging stuff
ADMIN_TOOL_APPS = (
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
)

# django
CORE_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # django admin
    'django.contrib.admin',
    'django.contrib.admindocs',
)

EXTERNAL_APPS = (
    'model_blocks',
    'django_extensions',
    'session_security',
    'extra_views',
    
)

AUTHENTICATION_APPS = (
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # ... include the providers you want to enable:
    # 'allauth.socialaccount.providers.amazon',
    # 'allauth.socialaccount.providers.angellist',
    # 'allauth.socialaccount.providers.bitbucket',
    # 'allauth.socialaccount.providers.bitly',
    # 'allauth.socialaccount.providers.dropbox',
    # 'allauth.socialaccount.providers.facebook',
    # 'allauth.socialaccount.providers.flickr',
    # 'allauth.socialaccount.providers.feedly',
    # 'allauth.socialaccount.providers.github',
    # 'allauth.socialaccount.providers.google',
    # 'allauth.socialaccount.providers.instagram',
    # 'allauth.socialaccount.providers.linkedin',
    # 'allauth.socialaccount.providers.linkedin_oauth2',
    # 'allauth.socialaccount.providers.openid',
    # 'allauth.socialaccount.providers.persona',
    # 'allauth.socialaccount.providers.soundcloud',
    # 'allauth.socialaccount.providers.stackexchange',
    # 'allauth.socialaccount.providers.tumblr',
    # 'allauth.socialaccount.providers.twitch',
    # 'allauth.socialaccount.providers.twitter',
    # 'allauth.socialaccount.providers.vimeo',
    # 'allauth.socialaccount.providers.vk',
    # 'allauth.socialaccount.providers.weibo',
 )

LOCAL_APPS = (
    'extra_fixtures',  # only holds /fixtures
    'contact_info',
    'common',
    'farms',
    'irrigator_pro',
    'notifications',
    'home',
)

# the order is important!
INSTALLED_APPS = LOCAL_APPS \
                 + ADMIN_TOOL_APPS \
                 + CORE_APPS \
                 + EXTERNAL_APPS \
                 + AUTHENTICATION_APPS


###
# Logging
###
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        # New in Django 1.5
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

###
# Email Settings
###

EMAIL_HOST           = 'localhost'
EMAIL_BACKEND        = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL   = 'webmaster@irrigatorpro.org'
SERVER_EMAIL         = 'webmaster@irrigatorpro.org'
# EMAIL_PORT           = ''
# EMAIL_HOST_USER      = ''
# EMAIL_HOST_PASSWORD  = ''
# EMAIL_USE_TLS        = ''

###
# Authenticationx Settings
###

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",

    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
)

ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = False
LOGIN_REDIRECT_URL = '/farm/report/summary_report/'
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/farm/settings/contact_info/'
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/farm/settings/contact_info/'
ACCOUNT_LOGIN_REDIRECT_URL = '/farm/settings/contact_info/'


ACCOUNT_AUTHENTICATION_METHOD = "email"      # User can login using either userid or email
ACCOUNT_EMAIL_REQUIRED        = True         # User is required to hand over an e-mail address when signing up.
ACCOUNT_EMAIL_VERIFICATION    = "mandatory"  # User is blocked from logging in until the email address is verified. 
ACCOUNT_USERNAME_REQUIRED     = False        # Do not prompt the user to enter a username
ACCOUNT_PASSWORD_MIN_LENGTH   = 8            # Minimum password length.
ACCOUNT_LOGOUT_ON_GET         = True         # User is automatically logged out by a mere GET request
ACCOUNT_USER_DISPLAY          = lambda user: user.email

###
# django-session-security Session Timeout Settings
###

# WARN_AFTER
#    Time (in seconds) before the user should be warned that is session will 
#    expire because of inactivity. Default 540. 
# SESSION_SECURITY_WARN_AFTER=540

# EXPIRE_AFTER
#    Time (in seconds) before the user should be logged out if inactive. Default
#    is 600. 
# SESSION_SECURITY_EXPIRE_AFTER=600

# PASSIVE_URLS
#    List of urls that should be ignored by the middleware. For example the 
#    ping ajax request of session_security is made without user intervention,
#    as such it should not be used to update the user's last activity datetime.
# SESSION_SECURITY_PASSIVE_URLS=[]

# EXPIRE_AT_BROWSER_CLOSE
#    Required for this module to operate properly
SESSION_EXPIRE_AT_BROWSER_CLOSE=True


###
## django-admin-tools Settings
###
ADMIN_TOOLS_THEMING_CSS = 'css/theming.css'

###
## Google Analytics 
##
# Google Analytics Key --  This is a placeholder to avoid errors if not set.
# Set the actual value in local.py
GA_KEY = ""   

###
## Setting for the notification emails. Actual values need to be set in local.py
###

NOTIFICATION_SMTP = ""
NOTIFICATION_HOST = ""
NOTIFICATION_PORT = ""

###
## Setting for the sms notification emails. Actual values need to be set in local.py
###
TWILIO_ACCOUNT_SID = ""
TWILIO_AUTH_TOKEN = ""
TWILIO_PHONE_NUMBER = ""

###
# This avoids warnings messages bout old test runner
###
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
