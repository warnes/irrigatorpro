#!/bin/bash

python manage.py dumpdata --indent 4 contact_info  > contact_info/fixtures/initial_data.json
python manage.py dumpdata --indent 4 farms         > farms/fixtures/initial_data.json
python manage.py dumpdata --indent 4 notifications > notifications/fixtures/initial_data.json
python manage.py dumpdata --indent 4 \
     --exclude contenttypes \
    account \
    auth.User \
    auth.Group \
    sites \
    > extra_fixtures/fixtures/initial_data.json