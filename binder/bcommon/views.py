# bcommon views

from bcommon.models import BindServer, Key
from django.template import Context
from django.shortcuts import render_to_response, redirect
from bcommon.helpers import list_zone_records, add_record, delete_record

from bcommon.forms import FormAddRecord
from django.template import RequestContext
from bcommon.keyutils import create_keyring

import re

RE_UNICODEARRAY = re.compile(r"u'(.*?)'")

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
    try:
        this_server = BindServer.objects.get(hostname=dns_hostname)
        zone_array = this_server.list_zones()
    except BindServer.DoesNotExist, err:
        return render_to_response('bcommon/list_server_zones.htm',
                                  { 'errors' : "The server %s does not exist in this Binder instance." % dns_hostname },
                                  context_instance=RequestContext(request))

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

def view_add_record(request, dns_server, zone):
    """ View to provide form to add a DNS record. """
    form = FormAddRecord(initial={ 'dns_server' : dns_server,
                                   'zone' : zone })
    return render_to_response('bcommon/add_record_form.htm',
                              { 'form' : form },
                              context_instance=RequestContext(request))

def view_add_record_result(request):
    """ Process the input given to add a DNS record. """
    if request.method == "GET":
        # Return home. You shouldn't be accessing this url via a GET.
        return redirect('/')

    form = FormAddRecord(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
    else:
        form = FormAddRecord(request.POST)
        return render_to_response('bcommon/add_record_form.htm',
                                  { 'form' : form },
                                  context_instance=RequestContext(request))


    add_record_response = add_record(cd)

    return render_to_response('bcommon/add_record_result.htm',
                              { 'response' : add_record_response },
                              context_instance=RequestContext(request))


def view_delete_record(request):
    if request.method == "GET":
        # Return home. You shouldn't trying to directly acces
        # the url for deleting records.
        return redirect('/')

    rr_server = request.POST['rr_server']
    rr_domain = request.POST['rr_domain']
    rr_array = request.POST.getlist('rr_array')

    return render_to_response('bcommon/delete_record_initial.htm',
                              { 'rr_server' : rr_server,
                                'rr_domain' : rr_domain,
                                'rr_array' :  rr_array,
                                'tsig_keys' : Key.objects.all() },
                              context_instance=RequestContext(request))


def view_delete_result(request):
    if request.method == "GET":
        # Return home. You shouldn't trying to directly access
        # the url for deleting records.
        return redirect('/')

    # What seems like an ugly hack to get around the fact
    # that the array comes back as Unicode values.
    rr_unicode_array = request.POST.getlist('rr_array')[0]
    rr_items = RE_UNICODEARRAY.findall(rr_unicode_array)

    delete_result = delete_record(request.POST, rr_items)

    return render_to_response('bcommon/delete_record_result.htm',
                              { 'delete_result' : delete_result },
                              context_instance=RequestContext(request))
