#!/usr/bin/env bash
# start-server.sh


exec gunicorn app:app \
    --bind 0.0.0.0:8080 \
    --workers 4 \
    --log-level=info \
    --log-file=/var/log/nginx/error.log \
    --access-logfile=/var/log/nginx/access.log \
"$@"