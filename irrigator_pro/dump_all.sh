#!/bin/bash

FILENAME=dumpdata_`date --rfc-3339=seconds | sed -e 's/ /_/g'`.json.bz2

echo "Dumping database contents to ${FILENAME}..."
python manage.py dumpdata \
    --natural-foreign \
    auth.User \
    auth.Group \
    sites \
    account \
    contact_info \
    farms        \
    notifications \
    $* \
    | bzip2 > $FILENAME
echo "Done."

## --exclude contenttypes \
