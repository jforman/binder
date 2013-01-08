#!/bin/bash -x

/usr/local/bin/fpm -t deb -s dir -n binder --verbose -v 1.0 \
  --package binder_trunk-`date '+%Y%m%d'`_all.deb -a all \
  --prefix /opt \
  -x '**.git**' \
  --url http://github.com/jforman/binder binder/