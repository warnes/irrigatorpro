from farms.models import *
from farms.generate_water_register import *
from datetime import date, datetime
from django.contrib.auth.models import User

field = Field.objects.get(name='East 1')
cs    = CropSeason.objects.get(name='Corn 2015', field_list=field)
day   = date.today()


user  = User.objects.get(email='greg@warnes.net')
today = date.today()

earliest_register_to_update( today, cs, field )

generate_water_register(cs, field, user)

earliest_register_to_update( today, cs, field )

field = Field.objects.get(pk=field.pk)
field.earliest_changed_dependency_date


now = datetime.now()
pr = ProbeReading(radio_id='ABC123_8', datetime=now, cuser_id=user.pk, muser_id=user.pk)
pr.soil_potential_8  = 100
pr.soil_potential_16 = 100
pr.soil_potential_24 = 100
pr.save()

earliest_register_to_update( today, cs, field )

generate_water_register(cs, field, user)


pr.soil_potential_8  = 10
pr.soil_potential_16 = 10
pr.soil_potential_24 = 00
pr.save()

earliest_register_to_update( today, cs, field )

generate_water_register(cs, field, user)

pr.soil_potential_8  = 0
pr.soil_potential_16 = 0
pr.soil_potential_24 = 0
pr.save()

earliest_register_to_update( today, cs, field )

generate_water_register(cs, field, user)



pr.reading_datetime = datetime.now() - timedelta(days=4)
pr.soil_potential_8  = 200
pr.soil_potential_16 = 200
pr.soil_potential_24 = 200
pr.save()
earliest_register_to_update( today, cs, field )


generate_water_register(cs, field, user)

earliest_register_to_update( today, cs, field )

pr.delete()
