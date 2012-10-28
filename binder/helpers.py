import keyutils

import re
import dns.query
import dns.reversename
import dns.update

import keyutils

re_IPADDRESS = re.compile(r"\d+.\d+.\d+.\d+")

class BinderException(Exception):
    pass

def list_zone_records(dns_server, zone_name):
    """Take a DNS server and a zone name,
    and return an array of its records."""
    # Need to move most of this logic into a helper method.
    try:
        zone = dns.zone.from_xfr(dns.query.xfr(dns_server, zone_name))
    except dns.exception.FormError:
        # There was an error querying the server for the specific zone.
        # Example: a zone that does not exist on the server.
        return { 'errors' : 'Encountered a FormError when querying %s on %s' % (zone_name, dns_server) }
    except socket.gaierror, err:
        # TODO: Need to better handle errors here.
        return { 'errors' : "Problems querying DNS server %s: %s" % (dns_server, err)  }

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

def add_forward_record(dns_server, zone_name, record_name, record_type, record_data, ttl, keyring):
    """Take in data from FormAddRecord and a keyring object,
    return a response from the DNS server about adding the record."""

    dns_update = dns.update.Update(zone_name, keyring = keyring)
    dns_update.replace(record_name, ttl, record_type, record_data)

    try:
        response = dns.query.tcp(dns_update, dns_server)
    except dns.tsig.BadPeerKey:
        raise BinderException("There was a problem adding your forward record due to a TSIG key issue.")

    return response

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
        keyring = keyutils.create_keyring(form_data["key_name"])
    else:
        keyring = None

    response = []
    response.append({ "type" : "Forward Record: %s.%s" % (str(form_data["record_name"]),
                                                          str(form_data["zone_name"])),
                      "output" : add_forward_record(str(form_data["dns_server"]),
                                                    str(form_data["zone_name"]),
                                                    str(form_data["record_name"]),
                                                    str(form_data["record_type"]),
                                                    str(form_data["record_data"]),
                                                    form_data["ttl"],
                                                    keyring)})

    if form_data["create_reverse"]:
        response.append({ "type" : "Reverse Record: %s" % form_data["record_data"],
                          "output" : add_reverse_record(str(form_data["dns_server"]),
                                                        str(form_data["zone_name"]),
                                                        str(form_data["record_name"]),
                                                        str(form_data["record_data"]),
                                                        form_data["ttl"],
                                                        keyring)})

    return response

def add_cname_record(dns_server, zone_name, originating_record, cname, ttl, key_name):
    """Add a Cname record."""

    if key_name is None:
        keyring = keyutils.create_keyring(key_name)
    else:
        keyring = None

    update = dns.update.Update(zone_name, keyring = keyring)
    update.replace(cname, int(ttl), 'CNAME', originating_record + ".")
    response = dns.query.tcp(update, dns_server)

    return response

def delete_record(form_data, rr_items):
    """Delete a list of DNS records passed as strings in rr_items."""

    if form_data["key_name"]:
        keyring = keyutils.create_keyring(form_data["key_name"])
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
        delete_response.append({ "rr_item" : current_rr_item, "output" : output })

    return delete_response
