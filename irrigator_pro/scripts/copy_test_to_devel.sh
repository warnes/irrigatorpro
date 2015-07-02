#!/bin/bash

sudo -u postgres pg_dump -C irpro_test  > /tmp/irpro_test.sql 
sudo -u postgres perl -p -e 's/test_user/dev_user/g;' /tmp/irpro_test.sql > /tmp/irpro_test.1.sql
sudo -u postgres perl -p -e 's/irpro_test/irpro_dev/g;' /tmp/irpro_test.1.sql > /tmp/irpro_dev.sql
sudo -u postgres dropdb 'irpro_dev'
sudo -u postgres psql < /tmp/irpro_dev.sql 

rm /tmp/irpro_test.sql 
rm /tmp/irpro_test.1.sql 
rm /tmp/irpro_dev.sql 