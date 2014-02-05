#!/bin/bash

python manage.py dumpdata --indent 4 farms > farms/fixtures/initial_data.json
python manage.py dumpdata --indent 4 admin emailuser > registration/fixtures/initial_data.json
python manage.py dumpdata --indent 4 contact_info > contact_info/fixtures/initial_data.json
