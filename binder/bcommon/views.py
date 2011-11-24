# bcommon views

from bcommon.models import BindServer, Key
from django.template import Context
from django.shortcuts import render_to_response, redirect
from bcommon.helpers import list_zone_records, add_record #, delete_record

from bcommon.forms import FormAddRecord
from django.template import RequestContext

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
    this_server = BindServer.objects.get(hostname=dns_hostname)
    zone_array = this_server.list_zones()
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


    key_dict = Key.objects.get(name=cd["key_name"])
    add_record_response = add_record(cd, key_dict)

    return render_to_response('bcommon/add_record_result.htm',
                              { 'response' : add_record_response },
                              context_instance=RequestContext(request))


### WORK ON BELOW
def confirm_delete_record(request):
    if request.method == "GET":
        # Return home. You shouldn't trying to directly acces
        # the url for deleting records.
        return redirect('/')

    rr_server = request.POST['rr_server']
    rr_domain = request.POST['rr_domain']
    rr_array = request.POST.getlist('rr_array')

    ## TODO(jforman): We need to handle the case where the POST data
    ## is somehow bad.
    return render_to_response('bcommon/delete_record_initial.htm',
                              { 'rr_server' : rr_server,
                                'rr_domain' : rr_domain,
                                'rr_array' :  rr_array,
                                'tsig_keys' : Key.objects.all() },
                              context_instance=RequestContext(request))

    # If we hit a case where we don't know what's going on.
    # return render_to_response('bcommon/index.htm',
    #                           { 'errors' : "We hit an unhandled exception in deleting your requested records." },
    #                           context_instance=RequestContext(request))

def delete_result(request):
    if request.method == "GET":
        # Return home. You shouldn't trying to directly acces
        # the url for deleting records.
        return redirect('/')

    to_delete_array = {}
    to_delete_array['rr_server'] = request.POST['rr_server']
    to_delete_array['rr_domain'] = request.POST['rr_domain']
    to_delete_array['rr_array'] = eval(request.POST.getlist('rr_array')[0])
    for current in to_delete_array['rr_array']:
        print "current: %s" % current

    to_delete_array['key_name'] = request.POST['key_name']
    to_delete_array['key_data'] = Key.objects.get(name=(to_delete_array['key_name'])).data
    delete_result = delete_record(to_delete_array)
