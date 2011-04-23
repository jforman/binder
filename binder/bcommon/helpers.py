import urllib2
from BeautifulSoup import BeautifulStoneSoup as BS
import re

def list_server_zones(dns_hostname):
    # I should take the dns_hostname here, get the object from the DB,
    # and use the status port attribute for the urllib2 query.
    myreq = urllib2.Request("http://%s:853" % dns_hostname)
    try:
        http_request = urllib2.urlopen(myreq)
    except urllib2.URLError, err_reason: # Error retrieving zone list.
        return { 'errors' : err_reason, 'error_context' : "Trying to retrieve zone list from %s" % dns_hostname }

    return_array = []
    xmloutput = http_request.read()
    mysoup = BS(xmloutput)
    zones = mysoup.findAll('zone')
    for current_zone in zones: # Interate over found zones
        zone_name = current_zone.find('name').contents[0]
        try: # Is this zone of 'IN' type?
            in_zone = re.search(r"(.*)\/IN", zone_name).group(1)
            return_array.append(in_zone)
        except:
            pass
    
    return return_array
