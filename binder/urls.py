from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),

    (r'^info/$', 'bcommon.views.list_servers'),
    (r'^info/(?P<dns_hostname>[a-zA-Z0-9.]+)/$', 'bcommon.views.list_server_zones'),
)
