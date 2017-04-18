#!/bin/bash

docker run -it --rm -v `pwd`:/code/ -w /code/ python:2.7 /bin/bash
