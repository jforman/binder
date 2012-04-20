# Binder #

Home: 
A Django web application for viewing and editing your BIND DNS zones.

## Requirements ##

Packages:

* [Django](http://www.djangoproject.com)
* Python
 * [python-beautifulsoup](http://www.crummy.com/software/BeautifulSoup/)
 * [python-dnspython](http://www.dnspython.org/)
 * python-sqlite (if you will be using sqlite during development)
* [Bind DNS Server](http://www.isc.org/software/bind). At least version 9.5.x, which is needed for gathering remote statistics.

## Installation & Configuration ##

### BIND Name Servers ###

In each of the BIND servers you wish to be able to query, the following stanza will be needed in your named.conf:
This tells BIND to publish statistics on all interfaces on tcp port 853. There is a simple ACL allowing localhost and the noted subnet, 10.10.0.0/24, to access statistics. This can be verified by querying your DNS server with your perferred web browser at [http://dnsserver:853](http://dnsserver:853/)

In each zone specification, you will need to determine how locked down you want zone updates and transfer to be.

    include "/etc/bind/dynzone.key";

    statistics-channels {
        inet * port 853 allow { 10.10.0.0/24; };
    };

    controls {
        inet * port 953 allow { 10.10.0.0/24; } keys { dynzone-key; };
    };

    zone "dynzone.yourdomain.org" IN {
        type master;
        file "/var/cache/bind/master/db.dynzone.yourdomain.org";
        allow-update { key dynzone-key; };
    };

Where /etc/bind/test.key:

    key dynzone-key {
        algorithm hmac-md5;
        secret "foobar...BhBrq+Ra3fBzhA4IWjXY85AVUdxkSSObbw3D30xgsf.....";
    };

### Django Application ###

Deploy the Django application as you see fit, and create the database via `manage.py syncdb`.

Using the Admin UI, add each DNS Server to the 'Bind Servers' model under the bcommon app.

Once you have completed this, surf over to the URL where the binder Django app is installed and enjoy. 

## Todo ##

* Associate Keys with DNS Servers
 * Should we auto-populate the DB with a DNS Server's zones upon add?
