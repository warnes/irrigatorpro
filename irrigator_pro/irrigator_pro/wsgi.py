"""
WSGI config for irrigator_pro project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os, site

## Add the irrigator_pro virtual environment
ABSOLUTE_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',))
site.addsitedir(os.path.join(ABSOLUTE_PROJECT_ROOT,
                '/VirtualEnvs/irrigator_pro/lib/python2.7/site-packages'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "irrigator_pro.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
