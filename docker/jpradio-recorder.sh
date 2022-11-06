#!/bin/bash

jpradio-recorder \
    --queries-path /data/jpradio-recorder/queries.json \
    --media-root /data/media \
    --platform-config-path /data/jpradio-recorder/config.json \
    --database-host "mongodb://docker_mongo_1:27017/"
