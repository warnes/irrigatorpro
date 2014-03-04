"""
WSGI config for irrigator_pro project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os, site, sys

## Add the irrigator_pro virtual environment
activate_this = '/prod/VirtualEnvs/irrigator_pro/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

## Setup django paths
PROJECT_ROOT      = '/prod/irrigator_pro'
SITE_PACKAGE_ROOT = '/prod/VirtualEnvs/irrigator_pro/lib/python2.7/site-packages'
print "ROOT=", PROJECT_ROOT
print "SITE_PACKAGE_ROOT=", SITE_PACKAGE_ROOT
sys.path.append(PROJECT_ROOT)
site.addsitedir(SITE_PACKAGE_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "irrigator_pro.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
