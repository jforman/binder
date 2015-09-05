from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),

    url(r'^$', 'binder.views.home_index', name="index"),
    url(r'^server_list/$', 'binder.views.view_server_list', name="server_list"),

    url(r'^info/(?P<dns_server>[a-zA-Z0-9.-]+)/$', 'binder.views.view_server_zones', name="server_zone_list"),
    url(r'^info/(?P<dns_server>[a-zA-Z0-9.-]+)/(?P<zone_name>[a-zA-Z0-9.-]+)/$', 'binder.views.view_zone_records', name="zone_list"),

    url(r'^add_record/(?P<dns_server>[a-zA-Z0-9.-]+)/(?P<zone_name>[a-zA-Z0-9.-]+)/$', 'binder.views.view_add_record', name="add_record"),
    url(r'^add_cname/(?P<dns_server>[a-zA-Z0-9.-]+)/(?P<zone_name>[a-zA-Z0-9.-]+)/(?P<record_name>.*?)/$', 'binder.views.view_add_cname_record', name="add_cname"),
    url(r'^delete_record/(?P<dns_server>[a-zA-Z0-9.-]+)/(?P<zone_name>[a-zA-Z0-9.-]+)/$', 'binder.views.view_delete_record', name="delete_record"),
)
