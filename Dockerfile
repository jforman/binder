FROM debian:jessie

MAINTAINER Jeffrey Forman <code@jeffreyforman.net>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python-pip

RUN git clone https://github.com/jforman/binder.git /opt/binder/

RUN pip install -r /opt/binder/requirements.txt

ENV	PYTHONPATH $PYTHONPATH:/opt/binder
ENV	DJANGO_SETTINGS_MODULE binder.settings

RUN ["/opt/binder/manage.py", "migrate"]
RUN ["/opt/binder/manage.py", "loaddata", "/opt/binder/binder/fixtures/initial_data.json"]

EXPOSE :8000

CMD ["/opt/binder/manage.py", "runserver", "0.0.0.0:8000"]
