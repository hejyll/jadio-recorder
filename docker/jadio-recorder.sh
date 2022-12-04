#!/bin/bash

jadio-recorder \
    --queries-path /data/jadio-recorder/queries.json \
    --media-root /data/media \
    --platform-config-path /data/jadio-recorder/config.json \
    --database-host "mongodb://docker_mongo_1:27017/"
