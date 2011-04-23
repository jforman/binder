# bcommon views

from bcommon.models import BindServer
from django.template import Context
from django.shortcuts import render_to_response, redirect

import urllib2
from BeautifulSoup import BeautifulStoneSoup as BS
import re

import dns.query
import dns.zone
import socket

def home_index(request):
    return render_to_response('index.htm')

def list_servers(request):
    server_list = BindServer.objects.all().order_by('hostname')
    return render_to_response('bcommon/list_servers.htm',
                              { 'server_list' : server_list })


def list_server_zones(request, dns_hostname):
    # I should take the dns_hostname here, get the object from the DB,
    # and use the status port attribute for the urllib2 query.
    myreq = urllib2.Request("http://%s:853" % dns_hostname)
    try:
        http_request = urllib2.urlopen(myreq)
    except urllib2.URLError, err_reason: # Error retrieving zone list.
        server_list = BindServer.objects.all().order_by('hostname')
        return render_to_response('bcommon/list_servers.htm',
                                  { 'server_list' : server_list,
                                    'errors' : err_reason,
                                    'error_context' : "Trying to retrieve zone list from %s" % dns_hostname})

    xmloutput = http_request.read()
    mysoup = BS(xmloutput)
    zones = mysoup.findAll('zone')
    zone_array = []
    for current_zone in zones: # Interate over found zones
        zone_name = current_zone.find('name').contents[0]
        try: # Is this zone of 'IN' type?
            in_zone = re.search(r"(.*)\/IN", zone_name).group(1)
            zone_array.append(in_zone)
        except:
            pass

    return render_to_response('bcommon/list_server_zones.htm',
                              { 'zone_array' : zone_array,
                                'dns_hostname' : dns_hostname })

def list_zone(request, dns_hostname, zone_name):
    try:
        zone = dns.zone.from_xfr(dns.query.xfr(dns_hostname, zone_name))
    except dns.exception.FormError:
        # There was an error querying the server for the specific zone.
        # Example: a zone that does not exist on the server.
        return redirect('/info/')
    except socket.gaierror, e:
        # TODO: Need to better handle errors here.
        print "Problems querying DNS server %s: %s\n" % (options.dns_server, e)
        return # Need to handle this situation when it can't query the NS.'

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

    return render_to_response('bcommon/list_zone.htm',
                              { 'record_array' : record_array,
                                'dns_hostname' : dns_hostname,
                                'rr_server' : dns_hostname,
                                'rr_domain' : zone_name})
