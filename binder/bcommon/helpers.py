from bcommon.keyutils import create_keyring

import re
import dns.query
import dns.reversename
import dns.update

def list_zone_records(dns_hostname, zone_name):
    """Take a DNS server and a zone name,
    and return an array of its records."""
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

def add_forward_record(form_data, zone_keyring):
    """Take in data from FormAddRecord and a keyring object,
    return a response from the DNS server about adding the record."""

    re_form_data = re.search(r"(\w+).(.*)", form_data["name"])
    hostname = re_form_data.group(1)
    domain = re_form_data.group(2)

    dns_update = dns.update.Update(domain, keyring = zone_keyring)
    dns_update.replace(hostname, int(form_data["ttl"]), str(form_data["record_type"]), str(form_data["data"]))

    try:
        response = dns.query.tcp(dns_update, form_data["dns_server"])
    except dns.tsig.BadPeerKey:
        response = "There was a problem adding your forward record due to a TSIG key issue."

    return response

def add_reverse_record(form_data, zone_keyring):

    reverse_ip_fqdn = str(dns.reversename.from_address(form_data["data"]))
    reverse_ip = re.search(r"([0-9]+).(.*).$", reverse_ip_fqdn).group(1)
    reverse_domain = re.search(r"([0-9]+).(.*).$", reverse_ip_fqdn).group(2)

    dns_update = dns.update.Update(reverse_domain, keyring = zone_keyring)
    dns_update.replace(reverse_ip, int(form_data["ttl"]), "PTR", str(form_data["name"]) + ".")

    response = dns.query.tcp(dns_update, form_data["dns_server"])

    return response

def add_record(form_data, key_dict):
    """Add a DNS record with data from a FormAddRecord object.
    If a reverse PTR record is requested, this will be added too."""

    keyring = create_keyring(key_dict)
    response = {}
    forward_response = add_forward_record(form_data, keyring)
    response["forward_response"] = forward_response

    if form_data["create_reverse"]:
        reverse_response = add_reverse_record(form_data, keyring)
        response["reverse_response"] = reverse_response

    return response
