# bcommon views

from bcommon.models import BindServer
from django.template import Context
from django.shortcuts import render_to_response

import urllib2
from BeautifulSoup import BeautifulStoneSoup as BS
import re

def list_servers(request):
    server_list = BindServer.objects.all().order_by('hostname')
    return render_to_response('bcommon/list_servers.htm',
                              { 'server_list' : server_list })


def list_server_zones(request, dns_hostname):
    # I should take the dns_hostname here, get the object from the DB,
    # and use the status port attribute for the urllib2 query.
    myreq = urllib2.Request("http://%s:853" % dns_hostname)
    http_request = urllib2.urlopen(myreq)
    xmloutput = http_request.read()
    mysoup = BS(xmloutput)
    zones = mysoup.findAll('zone')
    zone_array = []
    for current_zone in zones: # Interate over found zones
        zone_name = current_zone.find('name').contents[0]
        try: # Is this zone of 'IN' type
            in_zone = re.search(r"(.*)\/IN", zone_name).group(1)
            zone_array.append(in_zone)
        except:
            pass

    return render_to_response('bcommon/list_server_zones.htm',
                              { 'zone_array' : zone_array,
                                'dns_hostname' : dns_hostname })
