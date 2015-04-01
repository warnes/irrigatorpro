"""
Add user created by ('cuser') and modified by ('muser') foreign key
refs to all models that contain these fields.

Based on
  http://mindlace.wordpress.com/2012/10/19/automatically-associating-users-with-django-models-on-save/
  and https://gist.github.com/mindlace/3918300.

Which was in turn almost entirely taken from
  https://github.com/Atomidata/django-audit-log/blob/master/audit_log/middleware.py

"""
from django.db.models import signals
from django.utils.functional import curry
 
class AuditMiddleware(object):
    def process_request(self, request):
        if not request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            if hasattr(request, 'user') and request.user.is_authenticated():
                user = request.user
            else:
                user = None
 
            mark_whodid = curry(self.mark_whodid, user)
            signals.pre_save.connect(mark_whodid,  dispatch_uid = (self.__class__, request,), weak = False)
 
    def process_response(self, request, response):
        signals.pre_save.disconnect(dispatch_uid =  (self.__class__, request,))
        return response
 
    def mark_whodid(self, user, sender, instance, **kwargs):
        # if model instance has cuser_id and it is not set to a value..
        if not getattr(instance, 'cuser_id', None):
            instance.cuser = user
        
        if hasattr(instance,'muser_id'):
            if user is not None:
                instance.muser = user
