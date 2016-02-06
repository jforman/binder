# Binder #

[![Build Status](https://travis-ci.org/jforman/binder.svg?branch=master)](https://travis-ci.org/jforman/binder)
[![Code Health](https://landscape.io/github/jforman/binder/master/landscape.svg?style=flat)](https://landscape.io/github/jforman/binder/master)

A Django web application for viewing and editing BIND DNS zone records.

Binder supports adding and deleting DNS records (and eventually editing in place). TSIG-authenticated transfers and updates are supported.

## Requirements ##

Packages:

* [Django](http://www.djangoproject.com) >=1.8
* Python Modules
  * [pybindxml](https://pypi.python.org/pypi?name=pybindxml&:action=display): This is a shared library I wrote to scrape and stick into Python dict objects various server/zone data from a BIND DNS server.
  * Beautifulsoup4: This library is included as a dependency of pybindmlx when you  when you install pybindxml.
  * [python-dnspython](http://www.dnspython.org/)
  * [python-sqlite](http://docs.python.org/2/library/sqlite3.html) (If you will be using Sqlite for server and key storage)
* [Bind DNS Server](http://www.isc.org/software/bind). At least version 9.5.x, which provides instrumentation for gathering process and zone statistics remotely.

## Installation & Configuration ##

The Binder repository is housed in a [Github](http://github.com/jforman/binder) repository. The repo containts all the Django code and example configuration data for running Binder both in development and production.

To verify that required and optional dependencies are installed, execute [check-dependencies.py](https://github.com/jforman/binder/blob/master/check-dependencies.py). This script checks that various Python modules will import correctly.

Binder is intended to be installed into the /opt directory in /opt/binder. Forthcoming deb packages will provide for this easy installation and upgrades.

Provided under the config directory are various example configurations for runing Binder:

config/

* binder-apache.conf.dist: Name-based virtual host configuration for running Binder under Apache.
* django.wsgi: WSGI configuration file called by Apache to run Binder.
* binder-nginx.conf.dist: Name-based virtual host configuration for running Binder under Nginx using fcgi.
* binder-upstart.conf.dist: Ubuntu Upstart configuration file for starting Binder upon machine startup.

binder/

* local_settings.py: Local settings called by Binder templates for TTL choices, record types handled, etc.

The development server is run as most Django dev servers are run.

    /opt/binder/manage.py migrate
    /opt/binder/manage.py runserver

Once you have the Django server up and running, you will want to configure at least one BIND server in the Django Admin app. This includes a hostname, TCP statistics port and a default TSIG transfer key to be used when doing AXFR actions (if necessary).

Keys should also be created, if needed. The name of the key should match the contents of the below noted key file. Along side the name, key data and type should also be specified.

Once these two pieces of configuration are done, open up [http://yourserver:port/](http://yourserver:port) to access Binder and begin DNS zone management.

### BIND DNS Server ###

When Binder accesses your BIND DNS server, it first queries the statistics port to gather various zone information. This data includes zone name, view, and serial number. This is all configured by some of the following configuration examples.

#### named.conf ####

We must provide server statistics from the BIND process itself. This allows Binder to query BIND itself and get a list of zones, views, and other statistics.

    options {
      zone-statistics yes;
    }

    statistics-channels {
        inet * port 8053 allow { 10.10.0.0/24; };
    };

This tells bind to start an HTTP server on port 8053 on all interfaces, allowing 10.10.0.0/24 to make requests on this interface, http://${bind_server}:8053/. You will most likely want to narrow down the subset of hosts or subnets that can query BIND for this data. This data can be viewed via your choice of Browser, or read by your favorite programming language and progamatically processed by your choice of XML library.

    include "/etc/bind/dynzone.key";

This tells Bind to load a TSIG key from dynzone.key that can be referenced later in named.conf.

Moving on to zone declaration, determine how locked down you want zone updates and transfers to be. The following zone is defined to allow all zone transfers, but restrict updates to those provided with the dynzone-key TSIG key.

    zone "dynzone.yourdomain.org" IN {
        type master;
        file "/var/cache/bind/master/db.dynzone.yourdomain.org";
        allow-update { key dynzone-key; };
    };

#### /etc/bind/dynzone.key ####

Below are the entire contents of the dynzone.key file. This specifies the name, algorith and TSIG secret.

    key dynzone-key {
        algorithm hmac-md5;
        secret "foobar...BhBrq+Ra3fBzhA4IWjXY85AVUdxkSSObbw3D30xgsf.....";
    };

referenced as 'dynzone-key' in named.conf

### Related Configuration ###

#### Apache HTTPD ####

If you are using Apache to front-end your Binder Django app, the following two configuration files can be used as starting points.

[binder-apache.conf.dist](https://github.com/jforman/binder/blob/master/config/binder-apache.conf.dist): Apache virtual host configuration file to be inclued in your apache.conf. Values provide for Binder to run on its own virtual host, separate logs, etc

[django.wsgi](https://github.com/jforman/binder/blob/master/config/django.wsgi): WSGI configuration file used by Apache to run the actual Django app.

#### Nginx ####

[binder-nginx.conf.dist](https://github.com/jforman/binder/blob/master/config/binder-nginx.conf.dist): Nginx virtual host configuraiton. This configuration expects Django to be running in fcgi mode on port 4001 on 127.0.0.1.

#### Ubuntu Upstart ####

To have Binder start upon system boot, if you are running Ubuntu, I have provided an [example Upstart configurarton](https://github.com/jforman/binder/blob/master/config/binder-upstart.conf.dist) to be installed in /etc/init/.
