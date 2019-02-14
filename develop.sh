#!/bin/bash

docker build -t jforman/binder:latest .
docker run -it --rm -v `pwd`:/code/ -w /code/ jforman/binder:latest /bin/ash
