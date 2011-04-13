from bcommon.models import BindServer, Key, Zone
from django.contrib import admin

class ZoneAdmin(admin.ModelAdmin):
    list_display = [ 'zone_name',  'server']

class KeyAdmin(admin.ModelAdmin):
    list_display = [ 'name', 'data' ]

admin.site.register(BindServer)
admin.site.register(Key, KeyAdmin)
admin.site.register(Zone, ZoneAdmin)
