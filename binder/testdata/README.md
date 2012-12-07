Binder Test Data Readme
=======================

Description
-----------
Contained in this directory are the Bind configuration and zone files necessary to run the integration tests.

These configuration files were tested on a Ubuntu 12.10 x64 server running Bind 9.8.1.

### named.conf

Bind's standard configuration file for options and zone data.

This is expected to be installed in /etc/named/

## binder-test.key

TSIG key file used for securing zone transfers and updates. Key name contained is "test-key",
using the MD5 algorithm.

This is expected to be installed in /etc/named/

## domain1.local

Forward Zone file for domain 'domain1.local'. This contains no records initially on purpose.

This is expected to be installed in /var/lib/bind/

## db.10.254.1

Reverse zone file for domain 'domain1.local'. This contains no records initially on purpose.

This is expected to be installed in /var/lib/bind/
