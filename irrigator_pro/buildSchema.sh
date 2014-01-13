#!/bin/bash

java \
    -jar ~/src/schemaspy/target/schemaSpy.jar \
    -t sqlite-xerial \
    -db ~/Consulting/USDA_NationalPeanutResearchLaboratory/irrigator_pro/db.sqlite3 \
    -u warnes \
    -p cp078109 \
    -o schema \
    -hq \
    -dp ~/src/schemaspy/target/sqlite-jdbc.jar 
