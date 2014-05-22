"""
WSGI config for irrigator_pro project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os, os.path, site, sys, socket

# Add django root dir to python path 
PROJECT_ROOT      = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',))
print "PROJECT_ROOT=", PROJECT_ROOT
sys.path.append(PROJECT_ROOT)

# Add virtualenv dirs to python path
host = socket.gethostname()
print "HOSTNAME=%s" % host
if host=='irrigatorpro':
    VIRTUAL_ENV_ROOT = '/www/VirtualEnvs/irrigator_pro/'
else:
    VIRTUAL_ENV_ROOT = os.path.join( PROJECT_ROOT, 'VirtualEnvs', 'irrigator_pro')


print "VIRTUAL_ENV_ROOT='%s'" % VIRTUAL_ENV_ROOT
activate_this = os.path.join(VIRTUAL_ENV_ROOT, 'bin', 'activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

# Get settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "irrigator_pro.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
