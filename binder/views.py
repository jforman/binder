from django.template import Context
from django.shortcuts import redirect, render
from binder import forms, helpers, keyutils, models

import re

RE_UNICODEARRAY = re.compile(r"u'(.*?)'")

class BinderException(Exception):
    pass

def home_index(request):
    return render(request, 'index.htm')

def view_server_list(request):
    """ List the DNS servers configured in the Django DB. """
    server_list = models.BindServer.objects.all().order_by('hostname')
    return render(request, 'bcommon/list_servers.htm',
                  { "server_list" : server_list})

def view_server_zones(request, dns_server):
    """ Display the list of DNS zones a particular DNS host provides. """
    errors = ""
    zone_array = {}
    try:
        this_server = models.BindServer.objects.get(hostname=dns_server)
        zone_array = this_server.list_zones()
    except BindServer.DoesNotExist, err:
        errors = err

    if "errors" in zone_array:
        errors = zone_array["errors"]

    return render(request, 'bcommon/list_server_zones.htm',
                  { "errors" : errors,
                    "dns_server" : dns_server,
                    "zone_array" : zone_array})

def view_zone_records(request, dns_server, zone_name):
    """ Display the list of records for a a particular zone."""
    try:
        this_server = models.BindServer.objects.get(hostname=dns_server)
        zone_array = this_server.list_zone_records(zone_name)
    except Exception, err:
        # TODO: Use a custom exception here.
        return render(request, 'bcommon/list_zone.htm',
                      { 'errors' : err})

    return render(request, 'bcommon/list_zone.htm',
                  { 'zone_array' : zone_array,
                    'dns_server' : dns_server,
                    'zone_name' : zone_name})

def view_add_record(request, dns_server, zone_name):
    """ View to provide form to add a DNS record. """
    return render(request, 'bcommon/add_record_form.htm',
                  { "dns_server" : dns_server,
                    "zone_name" : zone_name,
                    "tsig_keys" : models.Key.objects.all() })

def view_add_record_result(request):
    """ Process the input given to add a DNS record. """
    if request.method == "GET":
        return redirect('/')

    form = forms.FormAddRecord(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        try:
            add_record_response = helpers.add_record(cd)
        except BinderException, error:
            pass
        return render(request, 'bcommon/response_result.htm',
                      { "errors" : error,
                        "response" : add_record_response })

    return render(request, 'bcommon/add_record_form.htm',
                  { "dns_server" : request.POST["dns_server"],
                    "zone_name" : request.POST["zone_name"],
                    "form_errors" : form.errors,
                    "form_data" : request.POST })

def view_add_cname_record(request, dns_server, zone_name, record_name):
    """ Process given input to add a CNAME pointer."""
    return render(request, "bcommon/add_cname_record_form.htm",
                  { "dns_server" : dns_server,
                    "originating_record" : "%s.%s" % (record_name, zone_name),
                    "zone_name" : zone_name,
                    "tsig_keys" : models.Key.objects.all() })

def view_add_cname_result(request):
    if request.method == "GET":
        return redirect('/')

    form = forms.FormAddCnameRecord(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        try:
            add_cname_response = helpers.add_cname_record(
                str(cd["dns_server"]),
                str(cd["zone_name"]),
                str(cd["originating_record"]),
                str(cd["cname"]),
                str(cd["ttl"]),
                str(cd["key_name"]))
        except BinderException, error:
            pass

        return render(request, 'bcommon/response_result.htm',
                      { 'errors' : error,
                        'response' : add_cname_response })

    return render(request, "bcommon/add_cname_record_form.htm",
                  { "dns_server" : request.POST["dns_server"],
                    "zone_name" : request.POST["zone_name"],
                    "record_name" : request.POST["cname"],
                    "originating_record" : request.POST["originating_record"],
                    "form_data" : request.POST,
                    "form_errors" : form.errors,
                    "tsig_keys" : models.Key.objects.all() })


def view_delete_record(request):
    if request.method == "GET":
        # Return home. You shouldn't trying to directly acces
        # the url for deleting records.
        return redirect('/')

    dns_server = request.POST['dns_server']
    zone_name = request.POST['zone_name']
    rr_array = request.POST.getlist('rr_array')

    return render(request, 'bcommon/delete_record_initial.htm',
                  { 'dns_server' : dns_server,
                    'zone_name' : zone_name,
                    'rr_array' :  rr_array,
                    'tsig_keys' : models.Key.objects.all() })


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
        delete_result = helpers.delete_record(request.POST, rr_items)
    except Exception, err:
        return render(request, 'bcommon/response_result.htm.htm',
                      { "errors" : err })

    return render(request, 'bcommon/response_result.htm',
                  { 'response' : delete_result })
