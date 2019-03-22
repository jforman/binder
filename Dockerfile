FROM python:3-alpine

MAINTAINER Jeffrey Forman <code@jeffreyforman.net>

WORKDIR /code
COPY . /code/

RUN apk add --no-cache nsd build-base python3-dev libffi-dev openssl-dev libc-dev libxslt-dev mariadb-connector-c-dev \
  && pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

RUN ["python", "manage.py", "makemigrations", "binder"]
RUN ["python", "manage.py", "migrate"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
