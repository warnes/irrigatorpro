from django.dispatch import receiver
from django.db.models.signals import *
from farms.models import *

## This signal handler records the (earliest) modification date of
## any object upon which calculation of WaterRegister entries
## depend.
@receiver(pre_save, sender=WaterHistory)
@receiver(pre_save, sender=ProbeReading)
@receiver(pre_save, sender=CropSeasonEvent)
@receiver(pre_save, sender=Probe)
@receiver(pre_save, sender=ProbeReading)
@receiver(pre_save, sender=CropSeason)

@receiver(pre_delete, sender=WaterHistory)
@receiver(pre_delete, sender=ProbeReading)
@receiver(pre_delete, sender=CropSeasonEvent)
@receiver(pre_delete, sender=Probe)
@receiver(pre_delete, sender=ProbeReading)
@receiver(pre_delete, sender=CropSeason)

## TODO
# - Grab the relevante date from the object rather than mdate
# - For pre_save, if instance.id exists, then the action is an undate
#   of an existing object, and it can be accessed via
#   'CLASS.object.get(pk=instance.id)'.  See
#   http://stackoverflow.com/questions/5582410/django-how-to-access-original-unmodified-instance-in-post-save-signal.
# - The final assignment needs to be made atomic.

def handle_post_save_signal(sender, instance, **kwargs):
    print "Class of instance", type(instance).__name__
    if isinstance(instance, WaterHistory):
        try:
            fields = instance.field_list.all()
        except:
            fields = []
        mdate = instance.mdate
    elif isinstance(instance, CropSeasonEvent):
        try:
            fields = [ instance.field ]
        except:
            fields = []
        mdate = instance.mdate
    elif isinstance(instance, Probe):
        try:
            fields = instance.field_list.all()
        except:
            fields = []
        mdate = instance.mdate
    elif isinstance(instance, ProbeReading):
        try:
            probe = ProbeReading.objects.get(radio_id=instance.radio_id)
            fields = probe.field_list
        except:
            fields = []
        mdate = instance.mdate
    if isinstance(instance, CropSeason):
        try:
            fields = instance.field_list.all()
        except:
            fields = []
        mdate = instance.mdate
    else:
        raise RuntimeError('Unexpected object of class ' + type(instance).__name__ ) 

    for field in fields:
        field = Field.objects.get(id=field.id)

        ## TODO: This needs to be made an atomic transaction.  See
        ## https://docs.djangoproject.com/en/1.8/topics/db/transactions/
        field.dependency_mdate = min( field.dependency_mdate, mdate)
