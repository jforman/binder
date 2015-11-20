FROM debian:jessie

MAINTAINER Jeffrey Forman <code@jeffreyforman.net>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y \
    git \
    python-bs4 \
    python-dev \
    python-django \
    python-dnspython \
    python-lxml \
    python-pip \
    python-sqlite 

RUN pip install \
    pybindxml

WORKDIR /opt

RUN git clone https://github.com/jforman/binder.git

env	PYTHONPATH $PYTHONPATH:/opt/binder
env	DJANGO_SETTINGS_MODULE binder.settings

run ["/opt/binder/manage.py", "migrate"]
run ["/opt/binder/manage.py", "loaddata", "/opt/binder/binder/fixtures/initial_data.json"]

expose :8000

CMD ["/opt/binder/manage.py", "runserver", "0.0.0.0:8000"]