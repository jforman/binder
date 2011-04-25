# bcommon views

from bcommon.models import BindServer, Key
from django.template import Context
from django.shortcuts import render_to_response, redirect
from bcommon.helpers import list_server_zones, list_zone_records, add_record

from bcommon.forms import FormAddRecord
from django.template import RequestContext


import dns.update
import dns.tsigkeyring

import socket

def home_index(request):
    return render_to_response('index.htm')

def list_servers(request):
    """ List the DNS servers configured in the Django DB. """
    server_list = BindServer.objects.all().order_by('hostname')
    return render_to_response('bcommon/list_servers.htm',
                              { 'server_list' : server_list },
                              context_instance=RequestContext(request))


def view_server_zones(request, dns_hostname):
    """ Display the list of DNS zones a particular DNS host provides. """
    zone_array = list_server_zones(dns_hostname)
    if 'errors' in zone_array:
        return render_to_response('bcommon/list_server_zones.htm',
                                  { 'errors' : zone_array['errors'],
                                  'error_context' : zone_array['error_context'] })

    return render_to_response('bcommon/list_server_zones.htm',
                              { 'zone_array' : zone_array,
                                'dns_hostname' : dns_hostname },
                              context_instance=RequestContext(request))

def view_zone_records(request, dns_hostname, zone_name):
    """ Display the list of records a particular zone on a DNS host provides. """
    record_array = list_zone_records(dns_hostname, zone_name)
    if 'errors' in record_array:
        return render_to_response('bcommon/list_server_zones.htm',
                                  { 'errors' : record_array['errors'],
                                  'error_context' : record_array['error_context']},
                                  context_instance=RequestContext(request))

    return render_to_response('bcommon/list_zone.htm',
                              { 'record_array' : record_array,
                                'dns_hostname' : dns_hostname,
                                'rr_server' : dns_hostname,
                                'rr_domain' : zone_name},
                              context_instance=RequestContext(request))

def view_add_record(request, dns_hostname, zone_name):
    """ View to provide form to add a DNS record. """
    form = FormAddRecord(initial={ 'dns_hostname' : dns_hostname,
                                   'rr_domain' : zone_name })
    return render_to_response('bcommon/add_record_form.htm',
                              { 'form' : form },
                              context_instance=RequestContext(request))

def add_record_result(request):
    """ Process the input given to add a DNS record. """
    if request.method == "GET":
        # Return home. You shouldn't be accessing the result
        # via a GET.
        return redirect('/')

    # We got a POST to add the result.
    form = FormAddRecord(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        response = add_record(cd)

    if 'errors' in response:
        return render_to_response('bcommon/add_record_result.htm',
                                  { 'errors' : response['errors'] },
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('bcommon/add_record_result.htm',
                                  { 'response' : response },
                                  context_instance=RequestContext(request))
