#!/bin/bash

python manage.py dumpdata --indent 4 farms > farms/fixtures/initial_data.json
