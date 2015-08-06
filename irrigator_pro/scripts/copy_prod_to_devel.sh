#!/bin/bash

sudo -u postgres pg_dump -C irpro_prod  > /tmp/irpro_prod.sql 
sudo -u postgres perl -p -e 's/prod_user/dev_user/g;' /tmp/irpro_prod.sql > /tmp/irpro_prod.1.sql
sudo -u postgres perl -p -e 's/irpro_prod/irpro_dev/g;' /tmp/irpro_prod.1.sql > /tmp/irpro_dev.sql
sudo -u postgres dropdb 'irpro_dev'
sudo -u postgres psql < /tmp/irpro_dev.sql 

rm /tmp/irpro_prod.sql 
rm /tmp/irpro_prod.1.sql 
rm /tmp/irpro_dev.sql 