from django.conf.urls.defaults import *
from django.conf import settings
import os

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'bcommon.views.home_index', name="index"),
    url(r'^server_list/$', 'bcommon.views.view_server_list', name="server_list"),

    url(r'^info/(?P<dns_server>[a-zA-Z0-9.-]+)/$', 'bcommon.views.view_server_zones', name="server_zones"),
    url(r'^info/(?P<dns_server>[a-zA-Z0-9.-]+)/(?P<zone_name>[a-zA-Z0-9.-]+)/$', 'bcommon.views.view_zone_records', name="zone_records"),

    url(r'^add_record/(?P<dns_server>[a-zA-Z0-9.-]+)/(?P<zone_name>[a-zA-Z0-9.-]+)/$', 'bcommon.views.view_add_record', name="add_record"),
    url(r'^add_record/result/$', 'bcommon.views.view_add_record_result'),

    url(r'^delete_record/$', 'bcommon.views.view_delete_record', name="delete_record"),
    url(r'^delete_record/result/$', 'bcommon.views.view_delete_result'),

    url(r'^add_cname/(?P<dns_server>[a-zA-Z0-9.-]+)/(?P<zone_name>[a-zA-Z0-9.-]+)/(?P<record_name>[a-zA-Z0-9-]+)/$', 'bcommon.views.view_add_cname_record'),
    url(r'^add_cname_record/result/$', 'bcommon.views.view_add_cname_result'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
                            (r'^files/(?P<path>.*)$', 'django.views.static.serve',
                             {'document_root' : settings.MEDIA_ROOT}
                             ))
