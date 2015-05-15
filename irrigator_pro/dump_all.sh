#!/bin/bash

FILENAME=dumpdata_`date --rfc-3339=seconds | sed -e 's/ /_/g'`.json.bz2

echo "Dumping database contents to ${FILENAME}..."
python manage.py dumpdata \
    --indent=4 \
    --natural-foreign  \
    --natural-primary \
    contact_info \
    farms        \
    notifications \
    --exclude contenttypes \
    account \
    auth.User \
    auth.Group \
    sites \
    $* \
    | bzip2 > $FILENAME
echo "Done."
