#!/bin/bash

if [ -x "`which fpm`" ]; then
echo "FPM found, attempting to build package."
else
echo "Unable to find 'fpm', which is required to build package tarball. See https://github.com/jordansissel/fpm."
    exit
fi

if [ -z "$1" ]; then
echo "No version number specified, using date instead as version string."
    version=`date "+%Y%m%d"`
else
echo "Package version specified as $1."
    version=$1
fi

package_name="binder-$version.tgz"

fpm -s dir -t tar -n binder \
    -v $version \
    --package $package_name \
    -x '**.git**' \
    --prefix binder \
    .

if [ $? -ne 0 ]; then
echo "fpm executed exited with an error. Package was not built correctly."
    exit
fi

echo "Package built as $package_name."
