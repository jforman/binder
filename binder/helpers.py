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
    """Take in data from FormAddRecord and a keyring object,
    return a response from the DNS server about adding the record."""

    dns_update = dns.update.Update(zone_name, keyring = keyring)
    dns_update.replace(record_name, ttl, record_type, record_data)
    output = dns.query.tcp(dns_update, dns_server)

    return output

def add_reverse_record(dns_server, zone_name, record_name, record_data, ttl, keyring):
    """ Given passed arguments, add/update a reverse PTR record."""
    reverse_ip_fqdn = str(dns.reversename.from_address(record_data))
    reverse_ip = re.search(r"([0-9]+).(.*).$", reverse_ip_fqdn).group(1)
    reverse_domain = re.search(r"([0-9]+).(.*).$", reverse_ip_fqdn).group(2)

    dns_update = dns.update.Update(reverse_domain, keyring = keyring)
    dns_update.replace(reverse_ip, ttl, "PTR", "%s.%s." % (record_name, zone_name))
    output = dns.query.tcp(dns_update, dns_server)

    return output

def add_record(form_data):
    """Add a DNS record with data from a FormAddRecord dict.
    If a reverse PTR record is requested, this will be added too."""

    if form_data["key_name"]:
        this_key = models.Key.objects.get(name=form_data["key_name"])
        keyring = keyutils.create_keyring(this_key.name, this_key.data)
    else:
        keyring = None

    response = []
    response.append({ "description" : "Forward Record Added: %(record_name)s.%(zone_name)s" % form_data,
                      "output" : add_forward_record(str(form_data["dns_server"]),
                                                    str(form_data["zone_name"]),
                                                    str(form_data["record_name"]),
                                                    str(form_data["record_type"]),
                                                    str(form_data["record_data"]),
                                                    form_data["ttl"],
                                                    keyring)})

    if form_data["create_reverse"]:
        response.append({ "description" : "Reverse Record Added: %(record_data)s" % form_data,
                          "output" : add_reverse_record(str(form_data["dns_server"]),
                                                        str(form_data["zone_name"]),
                                                        str(form_data["record_name"]),
                                                        str(form_data["record_data"]),
                                                        form_data["ttl"],
                                                        keyring)})

    return response

def add_cname_record(dns_server, zone_name, originating_record, cname, ttl, key_name):
    """Add a Cname record."""

    if key_name == "None":
        keyring = None
    else:
        this_key = models.Key.objects.get(name=key_name)
        keyring = keyutils.create_keyring(this_key.name, this_key.data)

    update = dns.update.Update(zone_name, keyring = keyring)
    update.replace(cname, ttl, 'CNAME', originating_record + ".")
    response = dns.query.tcp(update, dns_server)

    return [{ "description" : "CNAME %s.%s points to %s" % (cname, zone_name, originating_record),
              "output" : response}]


def delete_record(form_data, rr_items):
    """Delete a list of DNS records passed as strings in rr_items."""

    if form_data["key_name"]:
        this_key = models.Key.objects.get(name=form_data["key_name"])
        keyring = keyutils.create_keyring(this_key.name, this_key.data)
    else:
        keyring = None

    dns_server = form_data["dns_server"]
    delete_response = []
    for current_rr_item in rr_items:
        re_record = re.search(r"(\w+)\.(.*)$", current_rr_item)
        record = re_record.group(1)
        domain = re_record.group(2)
        dns_update = dns.update.Update(domain, keyring = keyring)
        dns_update.delete(record)
        output = dns.query.tcp(dns_update, dns_server)
        delete_response.append({ "description" : "Delete record %s" % current_rr_item,
                                 "output" : output })

    return delete_response
