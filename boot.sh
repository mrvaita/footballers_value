#!/bin/bash
if [ ! -f ./football_players.sqlite ]; then
    python populate_db.py
fi

gunicorn -b :5000 \
    --access-logfile - \
    --error-logfile - \
    --reload \
    --daemon \
    wsgi:server

python run_cron.py
