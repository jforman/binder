from django.conf.urls.defaults import *
from django.conf import settings
import os

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^$', 'bcommon.views.home_index'),
    (r'^info/$', 'bcommon.views.view_server_list'),

    (r'^info/(?P<dns_server>[a-zA-Z0-9.-]+)/$', 'bcommon.views.view_server_zones'),
    (r'^info/(?P<dns_server>[a-zA-Z0-9.-]+)/(?P<zone_name>[a-zA-Z0-9.-]+)/$', 'bcommon.views.view_zone_records'),

    (r'^add_record/(?P<dns_server>[a-zA-Z0-9.-]+)/(?P<zone>[a-zA-Z0-9.-]+)/$', 'bcommon.views.view_add_record'),
    (r'^add_record/result/$', 'bcommon.views.view_add_record_result'),

    (r'^delete_record/$', 'bcommon.views.view_delete_record'),
    (r'^delete_record/result/$', 'bcommon.views.view_delete_result'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^files/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root' : settings.MEDIA_ROOT}
         ))
