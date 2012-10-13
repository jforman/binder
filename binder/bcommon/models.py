from BeautifulSoup import BeautifulStoneSoup as BS
from django.db import models

import dns.query
import dns.zone
import re
import urllib2

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
            zone_name = current_zone.find("name").string.split("/IN")[0]
            zone_serial = current_zone.find("serial").string
            zone_class = current_zone.find("rdataclass").string
            if zone_class == "IN":
                return_array.append({"zone_name" : zone_name, "zone_serial" : zone_serial })

        return return_array

    def list_zone_records(self, zone):
        """Given a zone, produce an array of dicts containing
        each RR record and its attributes."""
        try:
            zone = dns.zone.from_xfr(dns.query.xfr(self.hostname, zone))
        except dns.exception.FormError, err:
            raise Exception("The zone requested %s is not found on %s." % (zone, self.hostname))

        names = zone.nodes.keys()
        names.sort()
        record_array = []
        for current_name in names:
            current_record = zone[current_name].to_text(current_name)
            for split_record in current_record.split("\n"): # Split the records on the newline
                record_array.append({'rr_name'  : split_record.split(" ")[0],
                                     'rr_ttl'  : split_record.split(" ")[1],
                                     'rr_class' : split_record.split(" ")[2],
                                     'rr_type'  : split_record.split(" ")[3],
                                     'rr_data'  : split_record.split(" ")[4]})
        return record_array

class Key(models.Model):
    name = models.CharField(max_length=50)
    data = models.CharField(max_length=150)
    algorithm = models.CharField(max_length=200, choices=TSIG_ALGORITHMS)

    def __unicode__(self):
        return self.name
