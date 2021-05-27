FROM debian:buster

RUN apt-get update -y && \
    apt-get install -y \
    python3.7 \
    python3-pip \
    python3.7-dev \
    git

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /footballers_value/requirements.txt

WORKDIR /footballers_value

RUN python3 -m pip install -U pip && \
    python3 -m pip install -r requirements.txt && \
    python3 -m pip install gunicorn

COPY great_expectations great_expectations
COPY queries queries
COPY transfermarkt transfermarkt
COPY collect_season.py config.py dashboard.py populate_db.py run_cron.py wsgi.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP wsgi.py
ENV DATABASE_URL sqlite:////data/football_players.sqlite

RUN adduser --disabled-password footballers_value
RUN chown -R footballers_value:footballers_value ./
USER footballers_value

EXPOSE 5000
CMD ["./boot.sh"]
