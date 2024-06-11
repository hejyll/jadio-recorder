#!/bin/bash

echo "[$(date)] start jadio-recorder-periodic" >> /var/log/jadio-recorder-periodic

/usr/local/bin/jadio-recorder \
    --queries-path /data/jadio-recorder/queries.json \
    --media-root /data/media \
    --platform-config-path /data/jadio-recorder/config.json \
    --database-host mongodb://docker-jadio-mongo-1:27017/ \
    &>> /var/log/jadio-recorder-periodic

echo "[$(date)] finish jadio-recorder-periodic" >> /var/log/jadio-recorder-periodic
