"""
WSGI config for irrigator_pro project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os, site

## Add the irrigator_pro virtual environment
PROJECT_ROOT      = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',))
SITE_PACKAGE_ROOT = os.path.join( PROJECT_ROOT, 'VirtualEnvs', 'irrigator_pro', 'lib', 'python2.7', 'site-packages')
print "ROOT=", PROJECT_ROOT
print "SITE_PACKAGE_ROOT=", SITE_PACKAGE_ROOT
site.addsitedir(SITE_PACKAGE_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "irrigator_pro.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
