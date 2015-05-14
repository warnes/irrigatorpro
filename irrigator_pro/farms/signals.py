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

@receiver(post_save, sender=WaterHistory)
@receiver(post_save, sender=ProbeReading)
@receiver(post_save, sender=CropSeasonEvent)
@receiver(post_save, sender=Probe)
@receiver(post_save, sender=ProbeReading)

@receiver(pre_delete, sender=WaterHistory)
@receiver(pre_delete, sender=ProbeReading)
@receiver(pre_delete, sender=CropSeasonEvent)
@receiver(pre_delete, sender=Probe)
@receiver(pre_delete, sender=ProbeReading)

def handle_post_save_signal(sender, **kwargs):
    instance = kwargs.get('instance')
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
    else:
        raise RuntimeException('Unexpected object of class ' + type(instance).__name__ ) 

    for field in fields:
        field = Field.objects.get(id=field.id)
        field.dependency_mdate = min( field.dependency_mdate, mdate)
