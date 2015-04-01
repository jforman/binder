### Binder Helpers

# Standard Imports
import binascii
import re
import socket
import sys

# 3rd Party
import dns.query
import dns.reversename
import dns.tsig
import dns.tsigkeyring
import dns.update

# App Imports
from binder import exceptions, models

def add_record(dns_server, zone_name, record_name, record_type, record_data, ttl, key_name, create_reverse=False):
    """ Parse passed elements and determine which records to create.

    Args:
      String dns_server
      String zone_name
      String record_name (just record name, not FQDN)
      String record_type (A, AAAA, etc)
      String record_data (IP address)
      Int ttl
      String key_name (from Key model)
      Boolean create_reverse (Whether to create a PTR record, default False)

    Return:
      Dict containing {description, output} from record creation
    """

    response = []
    response.append({ "description" : "Forward Record Creation: %s.%s" % (record_name, zone_name),
                      "output" : create_update(dns_server,
                                               zone_name,
                                               record_name,
                                               record_type,
                                               record_data,
                                               ttl,
                                               key_name)})

    """ If requested, create a reverse PTR record.
    Given the forward record created, resolve its underlying IP. Use that to create the reverse record.
    reverse_ip_fqdn ex: 5.0.20.10.in-addr.arpa.
    reverse_ip: 5
    reverse_domain: 0.20.10.in-addr.arpa.
    """
    if create_reverse:
        reverse_ip_fqdn = str(dns.reversename.from_address(record_data))
        # There must be a cleaner way to figure out the ip/domain
        # for this reverse DNS record parsing.
        reverse_ip = re.search(r"([0-9]+).(.*)$", reverse_ip_fqdn).group(1)
        reverse_domain = re.search(r"([0-9]+).(.*)$", reverse_ip_fqdn).group(2)
        response.append({ "description" : "Reverse Record Creation: %s" % record_data,
                          "output" : create_update(dns_server,
                                                   reverse_domain,
                                                   reverse_ip,
                                                   "PTR",
                                                   "%s.%s." % (record_name, zone_name),
                                                   ttl,
                                                   key_name)})

    return response

def add_cname_record(dns_server, zone_name, cname, originating_record, ttl, key_name):
    """Add a Cname record."""

    output = create_update(dns_server,
                           zone_name,
                           cname,
                           "CNAME",
                           originating_record + ".",
                           ttl,
                           key_name)

    return [{ "description" : "CNAME %s.%s points to %s" % (cname, zone_name, originating_record),
              "output" : output}]

def delete_record(dns_server, rr_list, key_name):
    """Delete a list of DNS records passed as strings in rr_items."""

    try:
        transfer_key = models.Key.objects.get(name=key_name)
    except models.Key.DoesNotExist:
        keyring = None
        algorithm = None
    else:
        keyring = transfer_key.create_keyring()
        algorithm = transfer_key.algorithm

    delete_response = []
    for current_rr in rr_list:
        record_list = current_rr.split(".", 1)
        record = record_list[0]
        domain = record_list[1]
        dns_update = dns.update.Update(domain, keyring=keyring, keyalgorithm=algorithm)
        dns_update.delete(record)
        output = send_dns_update(dns_update, dns_server, key_name)

        delete_response.append({ "description" : "Delete Record: %s" % current_rr,
                                 "output" : output })

    return delete_response

def create_update(dns_server, zone_name, record_name, record_type, record_data, ttl, key_name):
    """ Update/Create DNS record of name and type with passed data and ttl. """

    try:
        transfer_key = models.Key.objects.get(name=key_name)
    except models.Key.DoesNotExist:
        keyring = None
        algorithm = None
    else:
        keyring = transfer_key.create_keyring()
        algorithm = transfer_key.algorithm

    dns_update = dns.update.Update(zone_name, keyring=keyring, keyalgorithm=algorithm)
    dns_update.replace(record_name, ttl, record_type, record_data)
    output = send_dns_update(dns_update, dns_server, key_name)

    return output

def ip_info(host_name):
    """Create a dictionary mapping address types to their IP's.
    If an error is encountered, key to error is "Error".
    """
    info = []
    ipv4_count = 0
    ipv6_count = 0
    try:
        for s_family, s_type, s_proto, s_cannoname, s_sockaddr in socket.getaddrinfo(host_name, None):
            if s_family == 2 and s_type == 1:
                ipv4_count += 1
                info.append(["IPv4 (%d)" % ipv4_count, s_sockaddr[0]])
            if s_family == 10 and s_type == 1:
                ipv6_count += 1
                info.append(["IPv6 (%d)" % ipv6_count, s_sockaddr[0]])
    except socket.gaierror, err:
        info.append(["Error", "Unable to resolve %s: %s" % (host_name, err)])

    return info

def send_dns_update(dns_message, dns_server, key_name):
    """ Send DNS message to server and return response.

    Args:
        Update dns_update
        String dns_server
        String key_name

    Returns:
        String output
    """

    try:
        output = dns.query.tcp(dns_message, dns_server)
    except dns.tsig.PeerBadKey:
        output = ("DNS server %s is not configured for TSIG key: %s." %
                  (dns_server, key_name))
    except dns.tsig.PeerBadSignature:
        output = ("DNS server %s did like the TSIG signature we sent. Check key %s "
                  "for correctness." % (dns_server, key_name))

    return output
