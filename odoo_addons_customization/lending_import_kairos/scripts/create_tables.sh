#!/bin/bash


PATH_FILES="/opt/odoo_addons_customization/lending_import_kairos/scripts/schema.sql"
DATABASE="AUDISALUD"
FILE_MDB="/opt/odoo_addons_customization/lending_import_kairos/scripts/demo.mdb"

# Creo las tablas en la base
mdb-schema "$FILE_MDB" postgres | sudo su postgres -c "psql -d $DATABASE"