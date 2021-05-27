#!/bin/bash
if [ ! -f /data/football_players.sqlite ]; then
    python3 populate_db.py
fi

gunicorn -b :5000 \
    --access-logfile - \
    --error-logfile - \
    --reload \
    --daemon \
    wsgi:server

python3 run_cron.py
