# bcommon views

from bcommon.models import BindServer, Key
from django.template import Context
from django.shortcuts import render_to_response, redirect, render
from bcommon.helpers import add_record, delete_record, add_cname_record

from bcommon.forms import FormAddRecord, FormAddCnameRecord
from django.template import RequestContext
from bcommon.keyutils import create_keyring

import re

RE_UNICODEARRAY = re.compile(r"u'(.*?)'")

def home_index(request):
    return render_to_response('index.htm')

def view_server_list(request):
    """ List the DNS servers configured in the Django DB. """
    server_list = BindServer.objects.all().order_by('hostname')
    return render_to_response('bcommon/list_servers.htm',
                              { "server_list" : server_list},
                              context_instance=RequestContext(request))

def view_server_zones(request, dns_server):
    """ Display the list of DNS zones a particular DNS host provides. """
    try:
        this_server = BindServer.objects.get(hostname=dns_server)
        zone_array = this_server.list_zones()
    except BindServer.DoesNotExist, err:
        return render_to_response('bcommon/list_server_zones.htm',
                                  { 'errors' : "The server %s does not exist in this Binder instance." % dns_server },
                                  context_instance=RequestContext(request))

    if 'errors' in zone_array:
        return render_to_response('bcommon/list_server_zones.htm',
                                  { 'errors' : zone_array['errors'],
                                  'error_context' : zone_array['error_context'] })

    return render_to_response('bcommon/list_server_zones.htm',
                              { 'zone_array' : zone_array,
                                'dns_server' : dns_server },
                              context_instance=RequestContext(request))

def view_zone_records(request, dns_server, zone_name):
    """ Display the list of records for a a particular zone."""
    try:
        this_server = BindServer.objects.get(hostname=dns_server)
        zone_array = this_server.list_zone_records(zone_name)
    except Exception, err:
        # TODO: Use a custom exception here.
        return render_to_response('bcommon/list_zone.htm',
                                  { 'errors' : err},
                                  context_instance=RequestContext(request))

    return render_to_response('bcommon/list_zone.htm',
                              { 'zone_array' : zone_array,
                                'dns_server' : dns_server,
                                'zone_name' : zone_name},
                              context_instance=RequestContext(request))

def view_add_record(request, dns_server, zone_name):
    """ View to provide form to add a DNS record. """
    return render(request, 'bcommon/add_record_form.htm',
                  { "dns_server" : dns_server,
                    "zone_name" : zone_name })

def view_add_record_result(request):
    """ Process the input given to add a DNS record. """
    errors = None
    if request.method == "GET":
        return redirect('/')

    form = FormAddRecord(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        try:
          add_record_response = add_record(cd)
        except BinderException, errors:
          pass
        return render_to_response('bcommon/add_record_result.htm',
                                  { "errors" : errors,
                                    "response" : add_record_response },
                                  context_instance=RequestContext(request))

    return render(request, 'bcommon/add_record_form.htm',
                  { "dns_server" : request.POST["dns_server"],
                    "zone_name" : request.POST["zone_name"],
                    "form_errors" : form.errors,
                    "form_data" : request.POST })

def view_add_cname_record(request, dns_server, zone_name, record_name):
    """ Process given input to add a CNAME pointer."""
    return render_to_response("bcommon/add_cname_record_form.htm",
                              { "dns_server" : dns_server,
                                "zone_name" : zone_name,
                                "record_name" :  record_name,
                                "tsig_keys" : Key.objects.all() },
                              context_instance=RequestContext(request))


def view_add_cname_result(request):
    if request.method == "GET":
        # Return home. You shouldn't trying to directly access
        # the url for deleting records.
        return redirect('/')

    form = FormAddCnameRecord(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
    else:
        return "bad form" # TODO: Send back the form pre-populated with the error

    try:
        add_cname_response = add_cname_record(str(cd["dns_server"]),
                                              str(cd["zone_name"]),
                                              str(cd["originating_record"]),
                                              str(cd["cname"]),
                                              str(cd["ttl"]),
                                              str(cd["key_name"]))
    except Exception, err:
        return render_to_response('bcommon/add_cname_result.htm',
                                  { 'errors' : err,
                                    'rr_data' : cd },)

    return render_to_response('bcommon/add_cname_result.htm',
                              { 'response' : add_cname_response,
                                'rr_data' : cd },
                              context_instance=RequestContext(request))



def view_delete_record(request):
    if request.method == "GET":
        # Return home. You shouldn't trying to directly acces
        # the url for deleting records.
        return redirect('/')

    dns_server = request.POST['dns_server']
    zone_name = request.POST['zone_name']
    rr_array = request.POST.getlist('rr_array')

    return render_to_response('bcommon/delete_record_initial.htm',
                              { 'dns_server' : dns_server,
                                'zone_name' : zone_name,
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

    try:
        delete_result = delete_record(request.POST, rr_items)
    except Exception, err:
        return render_to_response('bcommon/delete_record_result.htm',
                                  { "errors" : err },
                                  context_instance=RequestContext(request))

    return render_to_response('bcommon/delete_record_result.htm',
                              { 'delete_result' : delete_result },
                              context_instance=RequestContext(request))
