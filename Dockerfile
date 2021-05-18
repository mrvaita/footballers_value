FROM ubuntu:18.04

RUN apt-get update -y && \
    apt-get install -y \
    python3.6 \
    python3-pip \
    python3.6-dev \
    git

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /footballers_value/requirements.txt

WORKDIR /footballers_value

RUN python3 -m pip install -U pip && \
    python3 -m pip install -r requirements.txt && \
    python3 -m pip install gunicorn

# Limit this copy exclusively to the necessary directories
COPY . /footballers_value
RUN chmod +x boot.sh

ENV FLASK_APP wsgi.py

RUN adduser --disabled-password footballers_value
RUN chown -R footballers_value:footballers_value ./
USER footballers_value

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
