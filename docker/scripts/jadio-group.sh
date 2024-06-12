#!/bin/bash

DATA_ROOT=/data
CONFIG_ROOT="${DATA_ROOT}/configs"

DB_HOST=mongodb://docker-jadio-mongo-1:27017/

COMMAND=/usr/local/bin/jadio

config_name=$(basename $1)

"${COMMAND}" group "${CONFIG_ROOT}/${config_name}" --db-host "${DB_HOST}"
