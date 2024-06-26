#!/bin/bash -e

DATA_ROOT=/data
SERVICE_CONFIG_PATH="${DATA_ROOT}/configs/service.json"
MEDIA_ROOT="${DATA_ROOT}/media"
RSS_ROOT="${DATA_ROOT}/rss"

DB_HOST=mongodb://docker-jadio-mongo-1:27017/
HTTP_HOST=http://localhost

LOG_PATH=/var/log/jadio-cron.log
COMMAND=/usr/local/bin/jadio

script=$0

echo "[$(date)] Start ${script}" >> ${LOG_PATH}

"${COMMAND}" record \
    --service-config-path "${SERVICE_CONFIG_PATH}" \
    --media-root "${MEDIA_ROOT}" \
    --db-host "${DB_HOST}" \
2>&1 | tee -a ${LOG_PATH}

"${COMMAND}" feed \
    --rss-root ${RSS_ROOT} \
    --media-root "${MEDIA_ROOT}" \
    --http-host "${HTTP_HOST}" \
    --db-host "${DB_HOST}" \
2>&1 | tee -a ${LOG_PATH}

echo "[$(date)] Finish ${script}" >> ${LOG_PATH}
