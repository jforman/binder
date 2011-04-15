# Binder #

Home: 
A Django web application for viewing and (hopefully some day) editing your BIND DNS Zones.

## Requirements ##

Packages:

* [Django](http://www.djangoproject.com)
* Python
 * [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/)
 * [dns python](http://www.dnspython.org/)
* [Bind DNS Server](http://www.isc.org/software/bind). At least version 9.5.x, which is needed for gathering remote statistics.

## Installation & Configuration ##

### BIND Name Servers ###

In each of the BIND servers you wish to be able to query, the following stanza will be needed in your named.conf:

    statistics-channels {
        inet * port 853 allow { localhost; 10.10.0.0/24; };
    };

This tells BIND to listen on all available interfaces on port 853. There is a simple ACL allowing localhost and the noted subnet, 10.10.0.0/24, to access statistics. This can be verified by querying your DNS server with your perferred web browser at [http://dnsserver:853](http://dnsserver:853/)

### Django Application ###

Deploy the Django application as you see fit, and create the database via `manage.py syncdb`.

Using the Admin UI, add each DNS Server to the 'Bind Servers' model under the bcommon app.

Once you have completed this, surf over to the URL where the binder Django app is installed and enjoy. 


## Todo ##

* Associate Keys with DNS Servers
 * Should we auto-populate the DB with a DNS Server's zones upon add?
