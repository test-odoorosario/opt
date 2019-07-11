#!/bin/bash

CSV_FILES="/tmp/kairos/csv"
FILE_MDB="/tmp/kairos/kairos.mdb"
# Permiso en directorio
sudo chmod 777 -R "/tmp"
# Por cada tabla creo un csv con los datos de cada una
for TT in $(mdb-tables "$FILE_MDB"); do
    mdb-export -d ';' -D '%Y-%m-%d %H:%M:%S' "$FILE_MDB" "$TT" > "$CSV_FILES/${TT}.csv"
done
