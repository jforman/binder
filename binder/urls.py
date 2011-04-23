from django.conf.urls.defaults import *
from django.conf import settings
import os

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^$', 'bcommon.views.home_index'),
    (r'^info/$', 'bcommon.views.list_servers'),
    (r'^info/(?P<dns_hostname>[a-zA-Z0-9.-]+)/$', 'bcommon.views.view_server_zones'),
    (r'^info/(?P<dns_hostname>[a-zA-Z0-9.-]+)/(?P<zone_name>[a-zA-Z0-9.-]+)/$', 'bcommon.views.list_zone'),
    (r'^add_record/(?P<dns_hostname>[a-zA-Z0-9.-]+)/(?P<zone_name>[a-zA-Z0-9.-]+)/$', 'bcommon.views.add_record'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', 
         {'document_root' : os.path.join(settings.SITE_ROOT, 'static')}),
    )
