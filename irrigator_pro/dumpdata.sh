#!/bin/bash

python manage.py dumpdata --indent 4 farms > farms/fixtures/initial_data.json
python manage.py dumpdata --indent 4 contact_info > contact_info/fixtures/initial_data.json
python manage.py dumpdata --indent 4 admin > admin/fixtures/initial_data.json
python manage.py dumpdata --indent 4 auth > auth/fixtures/initial_data.json
