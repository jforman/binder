### Binder VIews

# 3rd Party
from django.shortcuts import redirect, render

# App Imports
from binder import exceptions, forms, helpers, models
import local_settings

def home_index(request):
    """ List the main index page for Binder. """
    return render(request, "index.htm")

def view_server_list(request):
    """ List the DNS servers configured in the database. """
    server_list = models.BindServer.objects.all().order_by("hostname")
    server_info = []
    for current in server_list:
        server_info.append({"host_name" : current, "ip_address" : helpers.ip_info(current.hostname)})

    return render(request, "bcommon/list_servers.htm",
                  { "server_info" : server_info})

def view_server_zones(request, dns_server):
    """ Display the list of DNS zones a particular DNS host provides. """
    errors = ""
    zone_array = {}
    try:
        this_server = models.BindServer.objects.get(hostname=dns_server)
        zone_array = this_server.list_zones()
    except models.BindServer.DoesNotExist, err:
        errors = "There is no configured server by that name: %s" % dns_server
    except exceptions.ZoneException, err:
        errors = "Unable to list server zones. Error: %s" % err

    return render(request, "bcommon/list_server_zones.htm",
                  { "errors" : errors,
                    "dns_server" : dns_server,
                    "zone_array" : zone_array})

def view_zone_records(request, dns_server, zone_name):
    """ Display the list of records for a particular zone. """
    errors = ""
    zone_array = {}
    try:
        this_server = models.BindServer.objects.get(hostname=dns_server)
        zone_array = this_server.list_zone_records(zone_name)
    except exceptions.TransferException, err:
        return render(request, "bcommon/list_zone.htm",
                      { "errors" : err,
                        "zone_name" : zone_name,
                        "dns_server" : dns_server})
    except models.BindServer.DoesNotExist:
        errors = "Requesting a zone listing for a Bind server that is not configured: %s" % dns_server

    return render(request, "bcommon/list_zone.htm",
                  { "zone_array" : zone_array,
                    "dns_server" : dns_server,
                    "zone_name" : zone_name,
                    "errors" : errors})

def view_add_record(request, dns_server, zone_name):
    """ View to provide form to add a DNS record. """
    return render(request, "bcommon/add_record_form.htm",
                  { "dns_server" : dns_server,
                    "zone_name" : zone_name,
                    "tsig_keys" : models.Key.objects.all(),
                    "ttl_choices" : local_settings.TTL_CHOICES,
                    "record_type_choices" : local_settings.RECORD_TYPE_CHOICES,
                    })

def view_add_record_result(request):
    """ Process the input given to add a DNS record. """
    errors = ""
    if request.method == "GET":
        return redirect("/")

    if "HTTP_REFERER" in request.META:
        incoming_zone = request.META["HTTP_REFERER"].split("/")[-2]
        if ("in-addr.arpa" in incoming_zone) or ("ip6.arpa" in incoming_zone):
            form = forms.FormAddReverseRecord(request.POST)
        else:
            form = forms.FormAddForwardRecord(request.POST)
    else:
        form = forms.FormAddForwardRecord(request.POST)

    if form.is_valid():
        form_cleaned = form.cleaned_data
        try:
            response = helpers.add_record(form_cleaned["dns_server"],
                                          str(form_cleaned["zone_name"]),
                                          str(form_cleaned["record_name"]),
                                          str(form_cleaned["record_type"]),
                                          str(form_cleaned["record_data"]),
                                          form_cleaned["ttl"],
                                          form_cleaned["key_name"],
                                          form_cleaned["create_reverse"])
        except exceptions.RecordException, err:
            # TODO: Start using this exception.
            # What would cause this?
            errors = err

        return render(request, "bcommon/response_result.htm",
                      { "errors" : errors,
                        "response" : response })

    return render(request, "bcommon/add_record_form.htm",
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
                    "ttl_choices" : local_settings.TTL_CHOICES,
                    "tsig_keys" : models.Key.objects.all() })

def view_add_cname_result(request):
    """ Process input on the CNAME form and provide a response."""
    if request.method == "GET":
        return redirect("/")

    errors = ""
    add_cname_response = ""
    form = forms.FormAddCnameRecord(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        try:
            add_cname_response = helpers.add_cname_record(
                cd["dns_server"],
                cd["zone_name"],
                cd["cname"],
                str(cd["originating_record"]),
                cd["ttl"],
                cd["key_name"])
        except exceptions.RecordException, err:
            errors = err

        return render(request, "bcommon/response_result.htm",
                      {"response" : add_cname_response,
                       "errors" : errors })

    return render(request, "bcommon/add_cname_record_form.htm",
                  { "dns_server" : request.POST["dns_server"],
                    "zone_name" : request.POST["zone_name"],
                    "record_name" : request.POST["cname"],
                    "originating_record" : request.POST["originating_record"],
                    "form_data" : request.POST,
                    "form_errors" : form.errors,
                    "ttl_choices" : local_settings.TTL_CHOICES,
                    "tsig_keys" : models.Key.objects.all() })


def view_delete_record(request):
    """ Provide the initial form for deleting records. """
    if request.method == "GET":
        return redirect("/")

    dns_server = request.POST["dns_server"]
    zone_name = request.POST["zone_name"]
    rr_list = request.POST.getlist("rr_list")

    return render(request, "bcommon/delete_record_initial.htm",
                  { "dns_server" : dns_server,
                    "zone_name" : zone_name,
                    "rr_list" :  rr_list,
                    "tsig_keys" : models.Key.objects.all() })


def view_delete_result(request):
    """ View that deletes records and returns the response. """
    if request.method == "GET":
        return redirect("/")

    form = forms.FormDeleteRecord(request.POST)

    if form.is_valid():
        clean_form = form.cleaned_data
    else:
        # TODO: What situations would cause this form
        # not to validate?
        print "in view_delete_result, form errors: %r" % form.errors

    delete_result = helpers.delete_record(clean_form["dns_server"],
                                          clean_form["rr_list"],
                                          clean_form["key_name"])

    return render(request, "bcommon/response_result.htm",
                  { "response" : delete_result })
