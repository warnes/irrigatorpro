from django.dispatch import receiver
from django.db.models.signals import *
from farms.models import *
from irrigator_pro.settings import DEBUG


def minNone( *args ):
    args = filter( lambda x: x is not None, args)
    if args: 
        return min(args)
    else:
        return None


## From
## http://stackoverflow.com/questions/15624817/have-loaddata-ignore-or-disable-post-save-signals

from functools import wraps
def disable_for_loaddata(signal_handler):
    """
    Decorator that turns off signal handlers when loading fixture data.
    """

    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs.get('raw', None):
            return
        signal_handler(*args, **kwargs)
    return wrapper



## These signal handlers records the (earliest) relevant date of any
## created/changed/deleted object upon which calculation of
## WaterRegister entries depend.

@receiver(pre_save, sender=WaterHistory)
@receiver(pre_delete, sender=WaterHistory)
@disable_for_loaddata
def handler_WaterHistory(sender, instance, **kwargs):
    if instance.id: # save changes to existing object
        new_instance = instance
        old_instance = WaterHistory.objects.get(pk=instance.id)

        old_field=old_instance.field
        new_field=new_instance.field
        old_field.earliest_changed_dependency_date = minNone(old_field.earliest_changed_dependency_date, 
                                                             old_instance.datetime.date()
                                                             )
        new_field.earliest_changed_dependency_date = minNone(new_field.earliest_changed_dependency_date, 
                                                             new_instance.datetime.date()
                                                             )
        old_field.save()
        new_field.save()
    else:   
        try:
            field = instance.field
            if instance.datetime:
                field.earliest_changed_dependency_date = minNone(field.earliest_changed_dependency_date, 
                                                                 instance.datetime.date()
                                                                 )
            field.save()
        except ValueError:
            pass


@receiver(pre_save, sender=ProbeReading)
@receiver(pre_delete, sender=ProbeReading)
@disable_for_loaddata
def handler_ProbeReading(sender, instance, **kwargs):
    if instance.id: # save changes to existing object
        new_instance = instance
        old_instance = ProbeReading.objects.get(pk=instance.id)
        old_radio_id = old_instance.radio_id
        old_reading_date = old_instance.datetime.date()

        old_probes = Probe.objects.filter(radio_id=old_radio_id,
                                          crop_season__season_start_date__lte=old_reading_date,
                                          crop_season__season_end_date__gte=old_reading_date)

        for old_probe in old_probes:
            field=old_probe.field
            new_date = minNone(field.earliest_changed_dependency_date, 
                               old_instance.datetime.date() )
            field.earliest_changed_dependency_date = new_date
            if DEBUG: print "Field %s: %s --> %s " % (field, field.earliest_changed_dependency_date, new_date)
            field.save()

    this_radio_id = instance.radio_id
    this_reading_date = instance.datetime.date()

    new_probes = Probe.objects.filter(radio_id=this_radio_id,
                                      crop_season__season_start_date__lte=this_reading_date,
                                      crop_season__season_end_date__gte=this_reading_date)

    for new_probe in new_probes:
        field=new_probe.field
        new_date = minNone(field.earliest_changed_dependency_date, 
                           instance.datetime.date() )
        field.earliest_changed_dependency_date = new_date
        if DEBUG: print "Field %s: %s --> %s " % (field, field.earliest_changed_dependency_date, new_date)
        field.save()


@receiver(pre_save,   sender=CropSeasonEvent)
@receiver(pre_delete, sender=CropSeasonEvent)
@disable_for_loaddata
def handler_CropSeasonEvent(sender, instance, **kwargs):
    if instance.id: # save changes to existing object
        new_instance = instance
        old_instance = CropSeasonEvent.objects.get(pk=instance.id)
        old_instance.field.earliest_changed_dependency_date = old_instance.date
        old_instance.field.save()

    instance.field.earliest_changed_dependency_date = instance.date    
    instance.field.save()

@receiver(pre_save, sender=CropSeason)
@receiver(pre_delete, sender=CropSeason)
@disable_for_loaddata
def handler_CropSeason(sender, instance, **kwargs):
    if instance.id: # save changes to existing object
        new_instance = instance
        old_instance = CropSeason.objects.get(pk=instance.id)
    
        old_date = None
        new_date = None
        if old_instance.season_start_date != new_instance.season_start_date:
            old_date = minNone(old_date, old_instance.season_start_date)
            new_date = minNone(new_date, new_instance.season_start_date)

        if old_instance.season_end_date != new_instance.season_end_date:
            old_date = minNone(old_date, old_instance.season_end_date)
            new_date = minNone(new_date, new_instance.season_end_date)

        if old_instance.crop != new_instance.crop:
            old_date = old_instance.season_start_date
            new_date = new_instance.season_start_date

        if old_date is not None: 
            for field in old_instance.field_list.all():
                field.earliest_changed_dependency_date = minNone(field.earliest_changed_dependency_date, 
                                                                 old_date)
                field.save()

        if new_date is not None:
            for field in new_instance.field_list.all():
                field.earliest_changed_dependency_date = minNone(field.earliest_changed_dependency_date,
                                                                 new_date)
                field.save()


        removed_fields = set( old_instance.field_list.all() ) - \
                         set( new_instance.field_list.all() ) 

        added_fields   = set( new_instance.field_list.all() ) - \
                         set( old_instance.field_list.all() ) 
                         
        for field in removed_fields:
            field.earliest_changed_dependency_date = minNone(field.earliest_changed_dependency_date, 
                                                             old_instance.season_start_date)
            field.save()


        for field in added_fields:
            field.earliest_changed_dependency_date = minNone(field.earliest_changed_dependency_date, 
                                                             new_instance.season_start_date)
            field.save()

    else:
        pass


@receiver(post_save, sender=CropSeason)
@disable_for_loaddata
def handler_CropSeason_postsave(sender, instance, created, **kwargs):
    if created == True:
        for field in instance.field_list.all():
            field.earliest_changed_dependency_date = minNone(field.earliest_changed_dependency_date, 
                                                             instance.season_start_date)
            field.save()


@receiver(pre_save,   sender=Probe)
@receiver(pre_delete, sender=Probe)
@disable_for_loaddata
def handler_Probe(sender, instance,  **kwargs):
    if instance.id:  # save changes to existing object
        new_instance = instance
        old_instance = Probe.objects.get(pk=instance.id)

        old_radio_id = old_instance.radio_id
        old_season_start_date = old_instance.crop_season.season_start_date
        old_season_end_date   = old_instance.crop_season.season_end_date
        old_probereadings     = ProbeReading.objects.filter(radio_id=old_radio_id, 
                                                             datetime__range=(old_season_start_date,
                                                                                      old_season_end_date)
                                                             )
        if old_probereadings:
            old_earliest_probereading_date = old_probereadings.earliest('datetime').datetime.date();
        else: 
            old_earliest_probereading_date = None;

        new_radio_id = new_instance.radio_id
        new_season_start_date = new_instance.crop_season.season_start_date
        new_season_end_date   = new_instance.crop_season.season_end_date
        new_probereadings     = ProbeReading.objects.filter(radio_id=new_radio_id, 
                                                             datetime__range=(new_season_start_date,
                                                                                      new_season_end_date)
                                                             )
        if new_probereadings:
            new_earliest_probereading_date = new_probereadings.earliest('datetime').datetime.date();
        else: 
            new_earliest_probereading_date = None;

    
        if old_radio_id != new_radio_id:  # changed radioid
            if old_instance.id and old_instance.field:
                field=old_instance.field
                field.earliest_changed_dependency_date = minNone(field.earliest_changed_dependency_date, 
                                                                 old_earliest_probereading_date)
                field.save()

            if new_instance.id and new_instance.field:
                field=new_instance.field
                field.earliest_changed_dependency_date = minNone(field.earliest_changed_dependency_date, 
                                                                 new_earliest_probereading_date)
                field.save()

        old_field = old_instance.field
        new_field = new_instance.field
            
        if old_field:
            old_field.earliest_changed_dependency_date = minNone(old_field.earliest_changed_dependency_date, 
                                                                 old_earliest_probereading_date)
            old_field.save()

        if new_field:
            new_field.earliest_changed_dependency_date = minNone(new_field.earliest_changed_dependency_date, 
                                                                 new_earliest_probereading_date)
            new_field.save()

    else: # new object or delete object

        radio_id = instance.radio_id
        season_start_date = instance.crop_season.season_start_date
        season_end_date   = instance.crop_season.season_end_date
        probereadings     = ProbeReading.objects.filter(radio_id=radio_id, 
                                                             datetime__range=(season_start_date,
                                                                                            season_end_date)
                                                             )
        if probereadings:
            earliest_probereading_date = probereadings.earliest('datetime').datetime.date();
        else: 
            earliest_probereading_date = None;

        if instance.id and instance.field:
            field=instance.field
            field.earliest_changed_dependency_date = minNone(field.earliest_changed_dependency_date, 
                                                             earliest_probereading_date)
            field.save()
