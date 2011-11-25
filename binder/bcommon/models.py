from django.db import models

import dns.query
import dns.zone
import urllib2
from BeautifulSoup import BeautifulStoneSoup as BS
import re

TSIG_ALGORITHMS = (('hmac-md5', 'MD5'),('hmac-sha1', 'SHA1'),('hmac-224', 'SHA224'),('hmac-sha256', 'SHA256'),('hmac-sha384', 'SHA384'),('hmac-sha512', 'SHA512'))

class BindServer(models.Model):
    hostname = models.CharField(max_length=100)
    statistics_port = models.IntegerField()
    control_port = models.IntegerField()

    def __unicode__(self):
        return self.hostname

    def list_zones(self):
        """ Take a DNS server, and list the DNS zones it provides resolution for. """
        # I should take the dns_hostname here, get the object from the DB,
        # and use the status port attribute for the urllib2 query.
        myreq = urllib2.Request("http://%s:%s" % (self.hostname, self.statistics_port))
        try:
            http_request = urllib2.urlopen(myreq)
        except urllib2.URLError, err_reason: # Error retrieving zone list.
            return { 'errors' : err_reason, 'error_context' : "Trying to retrieve zone list from %s" % self.hostname }

        return_array = []
        xmloutput = http_request.read()
        mysoup = BS(xmloutput)
        zones = mysoup.findAll('zone')
        for current_zone in zones: # Interate over found zones
            zone_name = current_zone.find('name').contents[0]
            try: # Is this zone of 'IN' type?
                in_zone = re.search(r"(.*)\/IN", zone_name).group(1)
                return_array.append(in_zone)
            except:
                pass

        return return_array


class Key(models.Model):
    name = models.CharField(max_length=50)
    data = models.CharField(max_length=150)
    algorithm = models.CharField(max_length=200, choices=TSIG_ALGORITHMS)

    def __unicode__(self):
        return self.name
