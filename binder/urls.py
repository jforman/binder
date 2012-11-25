from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'binder.views.home_index', name="index"),
    url(r'^server_list/$', 'binder.views.view_server_list', name="server_list"),

    url(r'^info/(?P<dns_server>[a-zA-Z0-9.-]+)/$', 'binder.views.view_server_zones', name="server_zones"),
    url(r'^info/(?P<dns_server>[a-zA-Z0-9.-]+)/(?P<zone_name>[a-zA-Z0-9.-]+)/$', 'binder.views.view_zone_records', name="zone_records"),

    url(r'^add_record/(?P<dns_server>[a-zA-Z0-9.-]+)/(?P<zone_name>[a-zA-Z0-9.-]+)/$', 'binder.views.view_add_record', name="add_record_initial"),
    url(r'^add_record/result/$', 'binder.views.view_add_record_result', name="add_record_result"),

    url(r'^delete_record/$', 'binder.views.view_delete_record', name="delete_record_initial"),
    url(r'^delete_record/result/$', 'binder.views.view_delete_result', name="delete_record_result"),

    url(r'^add_cname/(?P<dns_server>[a-zA-Z0-9.-]+)/(?P<zone_name>[a-zA-Z0-9.-]+)/(?P<record_name>[a-zA-Z0-9-]+)/$', 'binder.views.view_add_cname_record', name="add_cname_initial"),
    url(r'^add_cname_record/result/$', 'binder.views.view_add_cname_result', name="add_cname_result"),
)
