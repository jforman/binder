# Binder #

[![Build Status](https://travis-ci.org/jforman/binder.svg?branch=master)](https://travis-ci.org/jforman/binder)
[![Code Health](https://landscape.io/github/jforman/binder/master/landscape.svg?style=flat)](https://landscape.io/github/jforman/binder/master)

A Django web application for viewing and editing BIND DNS zone records.

It has support for NSD-hosted DNS zones, but as NSD does not support dynamic updates,
that feature is not available.

## Download ##

```
git clone https://github.com/jforman/binder.git
```

## Requirements ##

The requirements.txt file has the necessary dependencies.

```
pip install -r requirements.txt
```

## Running Binder ##

Over the course of developing Binder, it has come to the fore that using a container makes
development and running Binder much easier.

### Local Sqlite database ###

```
docker run jforman/binder:latest
```
### Admin user ###

Default admin user for Binder is 'admin', and password is 'admin' as well.

### MySQL database ###

If you wish to use a MySQL database, the following structure works:
```
docker run -e 'DJANGO_DB_HOST=XXXX' -e 'DJANGO_DB_PASSWORD=YYYY' -e 'DJANGO_DB_NAME=ZZZZ' -e 'DJANGO_DB_USER=binder' jforman/binder:latest
```

The Django settings.py is configured to accept the following environment
variables when configuring a MySQL-based backend database.

* DJANGO_DB_HOST: IP address or Hostname of the MySQL database host. (Required)
* DJANGO_DB_NAME: Name of the MySQL database. (Required)
* DJANGO_DB_USER: Username to access the above database. (Optional. Default: binder)
* DJANGO_DB_PASSWORD: Binder Database password (Required)

If you wish to use MySQL as the backing database, you must specify all required
parameters.

### Manually ###

Or you can run Binder directly on your host using the Django devserver.

```
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Develop Binder

If you want to develop on Binder, I've tried to write down the steps I use.

`develop.sh` is a shell script that will start a Docker container based off the
same image as the one on Docker hub. Only this script will mount your
Binder code directory into /code in the container.

Before any development can commence, you will need to install the requirements.

From inside the container:

```
pip install -r requirements.txt
```

### Generating a new initial_data.json

Certain versions of Django cause changes in the schema of the admin table.
In this case, I've found a (perhaps less than proper) workflow for creating
a new initial_data.json file. This uses a local Sqlite database file for
bootstrapping.

```
python manage.py migrate
python manage.py createsuperuser
python manage.py dumpdata -o binder/fixtures/initial_data.json
```

### Encrypted TSIG Keys ###

Starting with version 1.5, TSIG keys inside the database are encrypted using the [Crytography](https://cryptography.io/en/latest/fernet/) library and Fernet facilities.

Normally on startup, a new Fernet encryption key is created. This will change upon reboot as the process dies and restarts.

If you wish to use a statically configured encryption/decryption key, one must pass the DJANGO_FERNET_KEY environment variable, containing this key string. This *should* be used in production. This key *MUST* be kept secret or your TSIG keys will be able to be decrypted.

## External configuration ##

Aside from the Binder application itself, other infrastructure is required
to make Binder useful.

### NSD DNS Server ###

If you wish to access an NSD DNS server, the credentials are expected to be found in `/creds` creds directory,
where each subdirectory matches the configured hostname.

For example, for NSD host ns1.university.edu, the NSD remote control certificates would be found at the following paths:

```
/creds/ns1.university.edu/nsd_control.key
/creds/ns1.university.edu/nsd_control.pem
```

### BIND DNS Server ###

When Binder accesses your BIND DNS server, it first queries the statistics port to gather zone information. This includes zone name, view, and serial number.

#### named.conf ####

We must provide server statistics from the BIND process itself. This allows Binder to query BIND itself and get a list of zones, views, and other statistics.

    options {
      zone-statistics yes;
    }

    statistics-channels {
        inet * port 8053 allow { 10.10.0.0/24; };
    };

This tells bind to start an HTTP server on port 8053 on all interfaces, allowing 10.10.0.0/24 to make requests on this interface, http://${bind_server}:8053/. You will most likely want to narrow down list of source hosts/IPs who can query BIND for this data.

It is smart to include your TSIG key in a separate file. This way if you choose to have specific ACLs for your named.conf that are different from your TSIG key, this can be done.

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

For information on TSIG see http://www.cyberciti.biz/faq/unix-linux-bind-named-configuring-tsig/ .


### Apache HTTPD ###

If you are using Apache to front-end your Binder Django app, the following two configuration files can be used as starting points.

[binder-apache.conf.dist](https://github.com/jforman/binder/blob/master/config/binder-apache.conf.dist): Apache virtual host configuration file to be inclued in your apache.conf. Values provide for Binder to run on its own virtual host, separate logs, etc

[django.wsgi](https://github.com/jforman/binder/blob/master/config/django.wsgi): WSGI configuration file used by Apache to run the actual Django app.

### Nginx ###

[binder-nginx.conf.dist](https://github.com/jforman/binder/blob/master/config/binder-nginx.conf.dist): Nginx virtual host configuraiton. This configuration expects Django to be running in fcgi mode on port 4001 on 127.0.0.1.

#### MySQL ###

If you choose to use MySQL as your backing datastore, the following commands
will help you get up and running quickly.

```
create database binder;

create user 'binder'@'%' identified by 'INSERTYOURPASSWORDHERE';

grant all privileges on binder.* to 'binder'@'%';

flush privileges;
```
