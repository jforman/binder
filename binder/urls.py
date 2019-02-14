from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import login
from django.contrib.auth.views import logout_then_login
from django.contrib.auth import views as auth_views
import binder.views
admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^accounts/login/$', auth_views.LoginView.as_view(), name='login'),
    url(r'^accounts/logout/$', logout_then_login, name='logout'),

    url(r'^$', binder.views.home_index, name="index"),
    url(r'^server_list/$', binder.views.view_server_list, name="server_list"),

    url(r'^info/(?P<dns_server>[a-zA-Z0-9.-]+)/$', binder.views.view_server_zones, name="server_zone_list"),
    url(r'^info/(?P<dns_server>[a-zA-Z0-9.-]+)/(?P<zone_name>[a-zA-Z0-9.-]+)/$', binder.views.view_zone_records, name="zone_list"),

    url(r'^add_record/(?P<dns_server>[a-zA-Z0-9.-]+)/(?P<zone_name>[a-zA-Z0-9.-]+)/$', binder.views.view_add_record, name="add_record"),
    url(r'^add_cname/(?P<dns_server>[a-zA-Z0-9.-]+)/(?P<zone_name>[a-zA-Z0-9.-]+)/(?P<record_name>.*?)/$', binder.views.view_add_cname_record, name="add_cname"),
    url(r'^delete_record/(?P<dns_server>[a-zA-Z0-9.-]+)/(?P<zone_name>[a-zA-Z0-9.-]+)/$', binder.views.view_delete_record, name="delete_record"),
    url(r'^edit_record/(?P<dns_server>[a-zA-Z0-9.-]+)/(?P<zone_name>[a-zA-Z0-9.-]+)/(?P<record_name>[\S+]+)/(?P<record_data>[\S+]+)/(?P<record_ttl>[\S+]+)/$', binder.views.view_edit_record, name="edit_record"),
]
