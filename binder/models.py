from BeautifulSoup import BeautifulStoneSoup as BS
from binder import exceptions
from django.db import models

import dns.query
import dns.tsig
import dns.zone
import keyutils
import urllib2

TSIG_ALGORITHMS = (('hmac-md5', 'MD5'),
                   ('hmac-sha1', 'SHA1'),
                   ('hmac-sha256', 'SHA256'),
                   ('hmac-sha384', 'SHA384'),
                   ('hmac-sha512', 'SHA512'))

class Key(models.Model):
    """ Class to store and reference TSIG keys.

    TODO: Should/Can we encrypt these DNS keys in the DB?
    """
    name = models.CharField(max_length=255)
    data = models.CharField(max_length=255)
    algorithm = models.CharField(max_length=255, choices=TSIG_ALGORITHMS)

    def __unicode__(self):
        return self.name


class BindServer(models.Model):
    """ Class to store DNS servers and attributes for referencing their
        statistics ports. Also reference FK for TSIG transfer keys,
        if required.
    """
    hostname = models.CharField(max_length=255)
    statistics_port = models.IntegerField()
    default_transfer_key = models.ForeignKey(Key, null=True, blank=True)

    def __unicode__(self):
        return self.hostname

    def list_zones(self):
        """ List the DNS zones and attributes.

        TODO: Parse these XML more intelligently. Grab the view name. Any other data available?

        Returns:
          List of Dicts { String zone_name, String zone_serial }
        """
        zone_req  = urllib2.Request("http://%s:%s" % (self.hostname, self.statistics_port))
        try:
            http_request = urllib2.urlopen(zone_req)
        except urllib2.URLError, err:
            raise exceptions.ZoneException(err)

        return_array = []
        xmloutput = http_request.read()
        mysoup = BS(xmloutput)
        zones = mysoup.findAll('zone')
        for current_zone in zones:
            zone_name = current_zone.find("name").string.split("/IN")[0]
            zone_serial = current_zone.find("serial").string
            zone_class = current_zone.find("rdataclass").string
            if zone_class == "IN":
                return_array.append({"zone_name" : zone_name, "zone_serial" : zone_serial })

        return return_array

    def list_zone_records(self, zone_name):
        """ List all records in a specific zone.

        TODO: Print out current_record in the loop and see if we can parse this more programatically,
              rather than just splitting on space. What is the difference between class and type?
        Arguments:
          String zone_name: Name of the zone

        Returns:
          List of Dicts { String rr_name, String rr_ttl, String rr_class, String rr_type, String rr_data }
        """

        if self.default_transfer_key:
            keyring = keyutils.create_keyring(self.default_transfer_key.name,
                                              self.default_transfer_key.data)
        else:
            keyring = None

        try:
            zone = dns.zone.from_xfr(dns.query.xfr(self.hostname, zone_name, keyring=keyring))
        except dns.exception.FormError, err:
            raise exceptions.TransferException("There was an error attempting to list zone records.")
        except dns.tsig.PeerBadKey:
            raise exceptions.TransferException("Unable to list zone records because of a TSIG key mismatch.")

        names = zone.nodes.keys()
        names.sort()
        record_array = []
        for current_name in names:
            current_record = zone[current_name].to_text(current_name)
            for split_record in current_record.split("\n"):
                current_record = split_record.split(" ")
                rr_dict = {}
                rr_dict["rr_name"] = current_record[0]
                rr_dict["rr_ttl"] = current_record[1]
                rr_dict["rr_class"] = current_record[2]
                rr_dict["rr_type"] = current_record[3]
                rr_dict["rr_data"] = current_record[4]

                record_array.append(rr_dict)

        return record_array

