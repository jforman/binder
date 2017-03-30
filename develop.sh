#!/bin/bash

docker run -it --rm -e NODB=1 -v `pwd`:/code/ -w /code/ python:2.7 /bin/bash
