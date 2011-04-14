# bcommon views

from bcommon.models import BindServer
from django.template import Context
from django.shortcuts import render_to_response

def list_servers(request):
    server_list = BindServer.objects.all().order_by('hostname')
    return render_to_response('bcommon/list_servers.htm',
                              { 'server_list' : server_list })
