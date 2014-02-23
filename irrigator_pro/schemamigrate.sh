#!/bin/bash
echo -n "farms: "
./manage.py schemamigration farms --auto
echo -n "contact_info: "
./manage.py schemamigration contact_info --auto
