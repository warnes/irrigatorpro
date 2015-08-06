#!/bin/bash

DUMPPATH=/www/prod/irrigator_pro/db_dump
FILENAME=psql_dump_`date --rfc-3339=seconds | sed -e 's/ /_/g'`.sql.bz2
HERE=${PWD}

cd /tmp
echo -n "Writing database data to ${DUMPPATH}/${FILENAME} .."
sudo -u postgres pg_dump -C irpro_prod  | bzip2 - -c  >"${DUMPPATH}/${FILENAME}"
echo "Done."
cd ${HERE}