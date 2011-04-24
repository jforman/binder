# bcommon views

from bcommon.models import BindServer
from django.template import Context
from django.shortcuts import render_to_response, redirect
from bcommon.helpers import list_server_zones

from bcommon.forms import FormAddRecord
from django.template import RequestContext

import dns.query
import dns.zone
import socket

def home_index(request):
    return render_to_response('index.htm')

def list_servers(request):
    server_list = BindServer.objects.all().order_by('hostname')
    return render_to_response('bcommon/list_servers.htm',
                              { 'server_list' : server_list },
                              context_instance=RequestContext(request))


def view_server_zones(request, dns_hostname):
    zone_array = list_server_zones(dns_hostname)
    if 'errors' in zone_array:
        return render_to_response('bcommon/list_server_zones.htm',
                                  { 'errors' : zone_array['errors'],
                                  'error_context' : zone_array['error_context'] })

    return render_to_response('bcommon/list_server_zones.htm',
                              { 'zone_array' : zone_array,
                                'dns_hostname' : dns_hostname },
                              context_instance=RequestContext(request))

def list_zone(request, dns_hostname, zone_name):
    # Need to move most of this logic into a helper method.
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
                                'rr_domain' : zone_name},
                              context_instance=RequestContext(request))

def add_record(request, dns_hostname, zone_name):
    form = FormAddRecord(initial={ 'dns_hostname' : dns_hostname,
                                   'rr_domain' : zone_name })
    return render_to_response('bcommon/add_record.htm',
                              { 'form' : form },
                              context_instance=RequestContext(request))

