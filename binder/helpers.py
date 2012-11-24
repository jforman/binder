from binder import keyutils, exceptions
# TODO: Start using exceptions here, force a record/add/delete on
#        an unresponsive Bind server.

import re
import dns.query
import dns.reversename
import dns.update

from binder import exceptions, models

re_IPADDRESS = re.compile(r"\d+.\d+.\d+.\d+")

def add_forward_record(dns_server, zone_name, record_name, record_type, record_data, ttl, keyring):
    """ Create a forward DNS record given passed arguments.

    Args:
      String dns_server
      String zone_name
      String record_name (just record name, not FQDN)
      String record_type (A, AAAA, etc)
      String record_data (IP address)
      Int ttl
      Dict keyring object

    Return:
      String representation of DNS update output from record creation.
    """

    dns_update = dns.update.Update(zone_name, keyring = keyring)
    dns_update.replace(record_name, ttl, record_type, record_data)
    output = dns.query.tcp(dns_update, dns_server)

    return output

def add_reverse_record(dns_server, zone_name, record_name, record_data, ttl, keyring):
    """ Create a reverse DNS record (PTR) given passed arguments.

    Args:
      String dns_server
      String zone_name
      String record_name (just record name, not FQDN)
      String record_type (A, AAAA, etc)
      String record_data (IP address)
      Int ttl
      Dict keyring object

    Return:
      String representation of DNS update output from record creation.
    """

    reverse_ip_fqdn = str(dns.reversename.from_address(record_data))
    reverse_ip = re.search(r"([0-9]+).(.*).$", reverse_ip_fqdn).group(1)
    reverse_domain = re.search(r"([0-9]+).(.*).$", reverse_ip_fqdn).group(2)

    dns_update = dns.update.Update(reverse_domain, keyring = keyring)
    dns_update.replace(reverse_ip, ttl, "PTR", "%s.%s." % (record_name, zone_name))
    output = dns.query.tcp(dns_update, dns_server)

    return output

def add_record(dns_server, zone_name, record_name, record_type, record_data, ttl, key_name, create_reverse):
    """ Create DNS record(s) given passed arguments.

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

    if key_name is None:
        keyring = None
    else:
        this_key = models.Key.objects.get(name=key_name)
        keyring = keyutils.create_keyring(this_key.name, this_key.data)

    response = []
    response.append({ "description" : "Forward Record Added: %s.%s" % (record_name, zone_name),
                      "output" : add_forward_record(dns_server,
                                                    zone_name,
                                                    record_name,
                                                    record_type,
                                                    record_data,
                                                    ttl,
                                                    keyring)})

    if create_reverse:
        response.append({ "description" : "Reverse Record Added: %s" % record_data,
                          "output" : add_reverse_record(dns_server,
                                                        zone_name,
                                                        record_name,
                                                        record_data,
                                                        ttl,
                                                        keyring)})

    return response

def add_cname_record(dns_server, zone_name, originating_record, cname, ttl, key_name):
    """Add a Cname record."""

    if key_name == "None":
        # TODO: Does this need to be changed to "key_name is None"
        keyring = None
    else:
        this_key = models.Key.objects.get(name=key_name)
        keyring = keyutils.create_keyring(this_key.name, this_key.data)

    update = dns.update.Update(zone_name, keyring = keyring)
    update.replace(cname, ttl, 'CNAME', originating_record + ".")
    response = dns.query.tcp(update, dns_server)

    return [{ "description" : "CNAME %s.%s points to %s" % (cname, zone_name, originating_record),
              "output" : response}]


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
