#!/bin/bash

# Usage: ./build-dpkg.sh $version $prefix
# Example: ./build-dpkg.sh 3.14 /usr/local

if [[ "$#" -lt 2 ]]; then
    echo "You did not provide enough command line parameters. Example: tagrelease-builddpkg \$version \$prefix"
    exit 1
fi

if [ -x "`which fpm`" ]; then
echo "FPM found, attempting to build package."
else
echo "Unable to find 'fpm', which is required to build package tarball. See https://github.com/jordansissel/fpm."
    exit 1
fi

version="$1"
package_name="binder-$version.deb"
prefix="$2"

git tag -a "v$version" -m "binder v$"

fpm -s dir -t deb -n binder \
    -v $version \
    --package $package_name \
    -x ".git" \
    --prefix "$prefix/binder" \
    `dirname $0`

if [ $? -ne 0 ]; then
echo "fpm executed exited with an error. Package was not built correctly."
    exit
fi

echo "Package built as $package_name."
echo "Don't forget to run 'git push --tags"