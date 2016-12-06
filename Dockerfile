FROM python:2.7

MAINTAINER Jeffrey Forman <code@jeffreyforman.net>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
     && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

RUN ["python", "manage.py", "migrate"]
RUN ["python", "manage.py", "loaddata", "binder/fixtures/initial_data.json"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
