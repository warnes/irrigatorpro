from django.dispatch import receiver
from django.db.models.signals import *
from farms.models import *
<<<<<<< .merge_file_Z5stEJ
from irrigator_pro.settings import DEBUG

## These signal handlers records the (earliest) relevant date of any
## created/changed/deleted object upon which calculation of
## WaterRegister entries depend.


def minNone( x, y ):
    if x is None:
        return y
    elif y is None:
        return x
    else:
        return min(x, y)
    

@receiver(pre_save, sender=WaterHistory)
@receiver(pre_delete, sender=WaterHistory)
def handler_WaterHistory(sender, instance, **kwargs):
    print "Entering handler_WaterHistory"
    if instance.id: # save changes to existing object
        new_instance = instance
        old_instance = WaterHistory.objects.get(pk=instance.id)

        # content items changed: date, rain, irrigation
        content_changed = old_instance.date       != new_instance.date or \
                          old_instance.rain       != new_instance.rain or \
                          old_instance.irrigation != new_instance.irrigation

        if True: #content_changed:
            for field in old_instance.field_list.all():
                field.earliest_changed_dependency_date = minNone(field.earliest_changed_dependency_date, 
                                                                 old_instance.date)
                field.save()

        # field list changed
        removed_fields = set( old_instance.field_list.all() ) - \
                         set( new_instance.field_list.all() ) 

        added_fields   = set( new_instance.field_list.all() ) - \
                         set( old_instance.field_list.all() ) 
                         
        for field in removed_fields:
            field.earliest_changed_dependency_date = minNone(field.earliest_changed_dependency_date, 
                                                             old_earliest_probereading_date)
            field.save()

        for field in added_fields:
            field.earliest_changed_dependency_date = minNone(field.earliest_changed_dependency_date, 
                                                             new_earliest_probereading_date)
            field.save()
    else:                                                         
        try:
            for field in instance.field_list.all():
                field.earliest_changed_dependency_date = minNone(field.earliest_changed_dependency_date, 
                                                                 instance.date)
                field.save()
        except ValueError:
            pass
    print "Exiting handler_WaterHistory"


@receiver(pre_save, sender=ProbeReading)
@receiver(pre_delete, sender=ProbeReading)
def handler_ProbeReading(sender, instance, **kwargs):
    if instance.id: # save changes to existing object
        new_instance = instance
        old_instance = ProbeReading.objects.get(pk=instance.id)
        old_radio_id = old_instance.radio_id
        old_probe = Probe.objects.get(radio_id=old_radio_id)
        for field in old_probe.field_list.all():
            field.earliest_changed_dependency_date = minNone(field.earliest_changed_dependency_date, 
                                                             old_instance.reading_datetime.date() )
            field.save()

    radio_id = instance.radio_id
    probe = Probe.objects.get(radio_id=radio_id)
    for field in probe.field_list.all():
        field.earliest_changed_dependency_date = minNone(field.earliest_changed_dependency_date,
                                                         instance.reading_datetime.date() )
        field.save()


@receiver(pre_save,   sender=CropSeasonEvent)
@receiver(pre_delete, sender=CropSeasonEvent)
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
        for field in instance.field_list.all():
            field.earliest_changed_dependency_date = minNone(field.earliest_changed_dependency_date, 
                                                             instance.season_start_date)
            field.save()


@receiver(pre_save,   sender=Probe)
@receiver(pre_delete, sender=Probe)
def handler_Probe(sender, instance, **kwargs):
    if instance.id:  # save changes to existing object
        new_instance = instance
        old_instance = Probe.objects.get(pk=instance.id)

        old_radio_id = old_instance.radio_id
        old_season_start_date = old_instance.crop_season.season_start_date
        old_season_end_date   = old_instance.crop_season.season_start_end
        old_earliest_probereading_date = ProbeReadings.objects.filter(radio_id=old_radio_id, 
                                                                      datetime__range=(old_season_start_date,
                                                                                       old_season_end_date)
                                                                      ).earliest('datetime').date()

        new_radio_id = new_instance.radio_id
        new_season_start_date = new_instance.crop_season.season_start_date
        new_season_end_date   = new_instance.crop_season.season_start_end
        new_earliest_probereading_date = ProbeReadings.objects.filter(radio_id=new_radio_id, 
                                                                      datetime__range=(new_season_start_date,
                                                                                       new_season_end_date)
                                                                      ).earliest('datetime').date()
    
        if old_radio_id != new_radio_id:  # changed radioid
            for field in old_instance.field_list.all():
                field.earliest_changed_dependency_date = minNone(field.earliest_changed_dependency_date, 
                                                                 old_earliest_probereading_date)
                field.save()

            for field in new_instance.field_list.all():
                field.earliest_changed_dependency_date = minNone(field.earliest_changed_dependency_date, 
                                                                 new_earliest_probereading_date)
                field.save()

        removed_fields = set( old_instance.field_list.all() ) - \
                         set( new_instance.field_list.all() ) 

        added_fields   = set( new_instance.field_list.all() ) - \
                         set( old_instance.field_list.all() ) 
                         
        for field in removed_fields:
            field.earliest_changed_dependency_date = minNone(field.earliest_changed_dependency_date, 
                                                             old_earliest_probereading_date)
            field.save()

        for field in added_fields:
            field.earliest_changed_dependency_date = minNone(field.earliest_changed_dependency_date, 
                                                             new_earliest_probereading_date)
            field.save()
    else: # new object or delete object
        radio_id = instance.radio_id
        season_start_date = instance.crop_season.season_start_date
        season_end_date   = instance.crop_season.season_end_date
        earliest_probereading_date = ProbeReading.objects.filter(radio_id=radio_id, 
                                                                 reading_datetime__range=(season_start_date, 
                                                                                          season_end_date)
                                                                 ).earliest('datetime').date()
    
        for field in instance.field_list.all():
            field.earliest_changed_dependency_date = minNone(field.earliest_changed_dependency_date, 
                                                             earliest_probereading_date)
            field.save()

=======

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
>>>>>>> .merge_file_O7RkyE
