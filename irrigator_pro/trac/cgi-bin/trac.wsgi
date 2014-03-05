import os, os.path, site, sys, socket

# Add django root dir to python path 
PROJECT_ROOT      = '/prod/irrigator_pro'
print "PROJECT_ROOT=", PROJECT_ROOT
sys.path.append(PROJECT_ROOT)

# Add virtualenv dirs to python path
if socket.gethostname()=='gregs-mbp':
    VIRTUAL_ENV_ROOT = os.path.join( PROJECT_ROOT, 'VirtualEnvs', 'irrigator_pro')
else:
    VIRTUAL_ENV_ROOT = '/prod/VirtualEnvs/irrigator_pro/'

print "VIRTUAL_ENV_ROOT='%s'" % VIRTUAL_ENV_ROOT
activate_this = os.path.join(VIRTUAL_ENV_ROOT, 'bin', 'activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "irrigator_pro.settings")
import irrigator_pro.settings

os.environ['TRAC_ENV'] = '/prod/irrigator_pro/trac'
os.environ['PYTHON_EGG_CACHE'] = '/prod/irrigator_pro/trac/eggs'

def application(environ, start_request):
    if not 'trac.env_parent_dir' in environ:
        environ.setdefault('trac.env_path', '/prod/irrigator_pro/trac')
    if 'PYTHON_EGG_CACHE' in environ:
        os.environ['PYTHON_EGG_CACHE'] = environ['PYTHON_EGG_CACHE']
    elif 'trac.env_path' in environ:
        os.environ['PYTHON_EGG_CACHE'] = \
            os.path.join(environ['trac.env_path'], '.egg-cache')
    elif 'trac.env_parent_dir' in environ:
        os.environ['PYTHON_EGG_CACHE'] = \
            os.path.join(environ['trac.env_parent_dir'], '.egg-cache')
    from trac.web.main import dispatch_request
    return dispatch_request(environ, start_request)

