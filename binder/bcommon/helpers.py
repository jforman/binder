import urllib2
from BeautifulSoup import BeautifulStoneSoup as BS
import re

from bcommon.models import Key, BindServer
import dns.query

def list_zone_records(dns_hostname, zone_name):
    """ Take a DNS zone, and list all the records it contains. """
    # Need to move most of this logic into a helper method.
    try:
        zone = dns.zone.from_xfr(dns.query.xfr(dns_hostname, zone_name))
    except dns.exception.FormError:
        # There was an error querying the server for the specific zone.
        # Example: a zone that does not exist on the server.
        return { 'errors' : 'Encountered a FormError when querying %s on %s' % (zone_name, dns_hostname) }
    except socket.gaierror, e:
        # TODO: Need to better handle errors here.
        return { 'errors' : "Problems querying DNS server %s: %s" % (dns_hostname, e)  }

    names = zone.nodes.keys()
    names.sort() # Sort the array alphabetically
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

def add_record(clean_data):
    key_name = Key.objects.get(name=(clean_data['tsig_key'])).name
    key_data = Key.objects.get(name=(clean_data['tsig_key'])).data
    key_algorithm = Key.objects.get(name=(clean_data['tsig_key'])).algorithm
    keyring = dns.tsigkeyring.from_text({ key_name : key_data })
    dns_update = dns.update.Update(clean_data['rr_domain'], keyring = keyring, keyalgorithm=key_algorithm)
    dns_update.replace(str(clean_data['rr_name']), 86400, str(clean_data['rr_type']), str(clean_data['rr_data']))
    try:
        response = dns.query.tcp(dns_update, clean_data['dns_hostname'])
    except dns.tsig.PeerBadKey:
        return {'errors' : "There was a problem adding your record due to a TSIG key issue. Please resolve that first." }

    return {'response' : response }
