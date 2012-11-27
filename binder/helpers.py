from binder import exceptions, keyutils, models

import dns.query
import dns.reversename
import dns.update
import dns.tsig
import socket
import re

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
      Boolean create_reverse

    Return:
      Dict containing {description, output} from record creation
    """

    response = []
    response.append({ "description" : "Forward Record Added: %s.%s" % (record_name, zone_name),
                      "output" : update_record(dns_server,
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
        response.append({ "description" : "Reverse Record Added: %s" % record_data,
                          "output" : update_record(dns_server,
                                                   reverse_domain,
                                                   reverse_ip,
                                                   "PTR",
                                                   "%s.%s." % (record_name, zone_name),
                                                   ttl,
                                                   key_name)})

    return response

def add_cname_record(dns_server, zone_name, cname, originating_record, ttl, key_name):
    """Add a Cname record."""

    output = update_record(dns_server,
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

    if key_name is None:
        keyring = None
    else:
        this_key = models.Key.objects.get(name=key_name)
        keyring = keyutils.create_keyring(this_key.name, this_key.data)

    delete_response = []
    for current_rr in rr_list:
        re_record = re.search(r"(\w+)\.(.*)$", current_rr)
        record = re_record.group(1)
        domain = re_record.group(2)
        dns_update = dns.update.Update(domain, keyring = keyring)
        dns_update.delete(record)
        output = dns.query.tcp(dns_update, dns_server)
        delete_response.append({ "description" : "Delete record %s" % current_rr,
                                 "output" : output })

    return delete_response

def update_record(dns_server, zone_name, record_name, record_type, record_data, ttl, key_name):
    """ Update/Create DNS record of name and type with passed data and ttl. """

    if key_name is None:
        keyring = None
    else:
        this_key = models.Key.objects.get(name=key_name)
        keyring = keyutils.create_keyring(this_key.name, this_key.data)

    dns_update = dns.update.Update(zone_name, keyring = keyring)
    dns_update.replace(record_name, ttl, record_type, record_data)
    output = dns.query.tcp(dns_update, dns_server)

    return output

def ip_info(host_name): # , family_dict, socket_dict):
    """Create a dictionary mapping address types to their IP's.
    If an error is encountered, key to error is "Error".
    """
    info = {}

    try:
        for s_family, s_type, s_proto, s_cannoname, s_sockaddr in socket.getaddrinfo(host_name.hostname, None):
            if s_family == 2 and s_type == 1:
                info["IPv4"] = s_sockaddr[0]
            if s_family == 10 and s_type == 1:
                info["IPv6"] = s_sockaddr[0]
    except socket.gaierror, err:
        info["Error"] = "Unable to resolve %s: %s" % (host_name, err)

    return info
