# Binder Views

import subprocess

# 3rd Party
import dns.query
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

# App Imports
from binder import forms, helpers, models
from binder import exceptions

def home_index(request):
    """List the main index page for Binder."""
    return render(request, "index.html")


def view_server_list(request):
    """List the DNS servers configured in the database."""
    server_list = models.BindServer.objects.all().order_by("hostname")
    server_info = []
    for current in server_list:
        server_info.append({"host_name": current,
                            "ip_address": helpers.ip_info(current.hostname),
                            "server_type": current.server_type})

    return render(request, "bcommon/list_servers.html",
                  {"server_info": server_info})


def view_server_zones(request, dns_server):
    """Display the list of DNS zones a particular DNS host provides."""
    zone_array = {}

    this_server = get_object_or_404(models.BindServer, hostname=dns_server)

    try:
        zone_array = this_server.list_zones()
    except exceptions.ZoneException as exc:
        messages.error(request, "Unable to list server zones. Error: %s" % exc)
    except subprocess.CalledProcessError as err:
        messages.error(request, "Error in retrieving zones: %s." % str(err.output))

    return render(request, "bcommon/list_server_zones.html",
                  {"dns_server": this_server,
                   "zone_array": zone_array})


def view_zone_records(request, dns_server, zone_name):
    """Display the list of records for a particular zone."""
    zone_array = {}

    this_server = get_object_or_404(models.BindServer, hostname=dns_server)

    try:
        zone_array = this_server.list_zone_records(zone_name)
    except exceptions.TransferException as exc:
        messages.error(request, "TransferException: %s." % exc)
        return render(request, "bcommon/list_zone.html",
                      {"zone_name": zone_name,
                       "dns_server": this_server})
    except exceptions.KeyringException:
        messages.error(request, "Unable to get zone list. A problem was encountered "
                       "decrypting your TSIG key. Ensure the key is correctly "
                       "specified in the Binder Database.")
        return render(request, "bcommon/list_zone.html",
                      { "dns_server": this_server,
                        "zone_name" :zone_name })
    except dns.query.TransferError as err:
        messages.error(request, "TransferError: %s." % err)
        return render(request, "bcommon/list_zone.html",
                      {"zone_name": zone_name,
                       "dns_server": this_server})

    return render(request, "bcommon/list_zone.html",
                  {"zone_array": zone_array,
                   "dns_server": this_server,
                   "zone_name": zone_name,
                   # NOTE: A hack because NSD doesn't support dynamic updates
                   # so merely display the zone.
                   "dynamic_dns_available": this_server.server_type in ['BIND']})


def view_add_record(request, dns_server, zone_name):
    """View to add an RR record to DNS zone."""
    this_server = get_object_or_404(models.BindServer, hostname=dns_server)
    if request.method == 'POST':
        if "in-addr.arpa" in zone_name or "ip6.arpa" in zone_name:
            form = forms.FormAddReverseRecord(request.POST)
        else:
            form = forms.FormAddForwardRecord(request.POST)
        if form.is_valid():
            form_cleaned = form.cleaned_data
            try:
                helpers.add_record(form_cleaned["dns_server"],
                                   str(form_cleaned["zone_name"]),
                                   str(form_cleaned["record_name"]),
                                   str(form_cleaned["record_type"]),
                                   str(form_cleaned["record_data"]),
                                   form_cleaned["ttl"],
                                   form_cleaned["key_name"],
                                   form_cleaned["create_reverse"])
            except (exceptions.KeyringException,
                    exceptions.RecordException) as exc:
                messages.error(request, "Adding %s.%s failed: %s" %
                               (form_cleaned["record_name"], zone_name, exc))
            else:
                messages.success(request, "%s.%s was added successfully." %
                                 (form_cleaned["record_name"], zone_name))
                return redirect('zone_list',
                                dns_server=dns_server,
                                zone_name=zone_name)
        else:
            messages.error(request, "Form data was invalid. Check all inputs.")
    else:
        # TODO: do this key_id logic on all forms for default key.
        key_id = models.BindServer.objects.get(
            hostname=dns_server).default_transfer_key.id
        form = forms.FormAddForwardRecord(initial={
                                            'zone_name': zone_name,
                                            'key_name': key_id
                                            })

    return render(request, "bcommon/add_record_form.html",
                  {"dns_server": this_server,
                   "form": form})

def view_edit_record(request, dns_server, zone_name, record_name=None,
                     record_type=None, record_data=None, record_ttl=None):
    """View to edit an RR record to DNS zone."""
    this_server = get_object_or_404(models.BindServer, hostname=dns_server)
    if request.method == 'POST':
        if "in-addr.arpa" in zone_name or "ip6.arpa" in zone_name:
            form = forms.FormAddReverseRecord(request.POST)
        else:
            form = forms.FormAddForwardRecord(request.POST)
        if form.is_valid():
            form_cleaned = form.cleaned_data
            try:
                helpers.add_record(form_cleaned["dns_server"],
                                   str(form_cleaned["zone_name"]),
                                   str(form_cleaned["record_name"]),
                                   str(form_cleaned["record_type"]),
                                   str(form_cleaned["record_data"]),
                                   form_cleaned["ttl"],
                                   form_cleaned["key_name"],
                                   form_cleaned["create_reverse"])
            except (exceptions.KeyringException,
                    exceptions.RecordException) as exc:
                messages.error(request, "Modifying %s.%s failed: %s" %
                               (form_cleaned["record_name"], zone_name, exc))
            else:
                messages.success(request, "%s.%s was modified successfully." %
                                 (form_cleaned["record_name"], zone_name))
                return redirect('zone_list',
                                dns_server=dns_server,
                                zone_name=zone_name)
        else:
            messages.error(request, "Form data was invalid. Check all inputs.")
    else:
        key_id = models.BindServer.objects.get(
            hostname=dns_server).default_transfer_key.id
        form = forms.FormAddForwardRecord(initial={'zone_name': zone_name,
                                                   'record_name': record_name,
                                                   'record_data': record_data,
                                                   'ttl': record_ttl,
                                                   'record_type': record_type,
                                                   'key_name': key_id
        })

    return render(request, "bcommon/add_record_form.html",
                  {"dns_server": this_server,
                   "form": form})


def view_add_cname_record(request, dns_server, zone_name, record_name):
    """View to allow to add CNAME records."""
    this_server = get_object_or_404(models.BindServer, hostname=dns_server)

    if request.method == 'POST':
        form = forms.FormAddCnameRecord(request.POST)
        if form.is_valid():
            form_cleaned = form.cleaned_data
            try:
                helpers.add_cname_record(form_cleaned["dns_server"],
                                         str(form_cleaned["zone_name"]),
                                         str(form_cleaned["cname"]),
                                         '%s.%s' % (str(form_cleaned["originating_record"]),
                                                    str(form_cleaned["zone_name"])),
                                         form_cleaned["ttl"],
                                         form_cleaned["key_name"])
            except (exceptions.KeyringException,
                    exceptions.RecordException) as exc:
                messages.error(request, "Adding %s.%s failed: %s" %
                               (form_cleaned["cname"], zone_name, exc))
            else:
                messages.success(request, "%s.%s was added successfully." %
                                 (form_cleaned["cname"], zone_name))
                return redirect('zone_list',
                                dns_server=dns_server,
                                zone_name=zone_name)
    else:
        key_id = models.BindServer.objects.get(
            hostname=dns_server).default_transfer_key.id
        form = forms.FormAddCnameRecord(initial={
            'originating_record': record_name,
            'zone_name': zone_name,
            'key_name': key_id})

    return render(request, "bcommon/add_cname_record_form.html",
                  {"dns_server": this_server,
                   "form": form})


def view_delete_record(request, dns_server, zone_name):
    """View to handle the deletion of records."""
    dns_server = models.BindServer.objects.get(hostname=dns_server)
    rr_list = request.POST.getlist("rr_list")

    if len(rr_list) == 0:
        messages.error(request, "Select at least one record for deletion.")
        return redirect('zone_list',
                        dns_server=dns_server,
                        zone_name=zone_name)

    if request.method == 'POST':
        form = forms.FormDeleteRecord(request.POST)
        if form.is_valid():
            form_cleaned = form.cleaned_data
            rr_list = form_cleaned["rr_list"]
            try:
                response = helpers.delete_record(form_cleaned["dns_server"],
                                                 rr_list,
                                                 form_cleaned["key_name"])
            except exceptions.KeyringException as exc:
                for record in rr_list:
                    messages.error(request, "Deleting %s.%s failed: %s" %
                                   (record, zone_name, exc))
            else:
                for record in response:
                    if record['success'] == True:
                        messages.success(request, "%s.%s was removed successfully." %
                                         (record['record'], zone_name))
                    else:
                        messages.error(request, "Deleting %s.%s failed: %s" %
                                       (record['record'], zone_name, record['description']))
                return redirect('zone_list',
                                dns_server=dns_server,
                                zone_name=zone_name)
    else:
        key_id = models.BindServer.objects.get(
            hostname=dns_server).default_transfer_key.id
        form = forms.FormDeleteRecord(initial={
            'zone_name': zone_name,
            'key_name': key_id
            })

    return render(request, "bcommon/delete_record.html",
                  {"dns_server": dns_server,
                   "zone_name": zone_name,
                   "rr_list": rr_list,
                   "form": form})
