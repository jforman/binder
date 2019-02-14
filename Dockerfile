FROM python:3-alpine

MAINTAINER Jeffrey Forman <code@jeffreyforman.net>

WORKDIR /code
COPY . /code/

RUN apk add --no-cache nsd build-base python3-dev libffi-dev openssl-dev libc-dev libxslt-dev \
  && pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

RUN ["python", "manage.py", "migrate"]
RUN ["python", "manage.py", "loaddata", "binder/fixtures/initial_data.json"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
