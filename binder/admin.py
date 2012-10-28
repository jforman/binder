from models import BindServer, Key
from django.contrib import admin

class ZoneAdmin(admin.ModelAdmin):
    list_display = [ 'zone_name',  'server', 'key' ]

class KeyAdmin(admin.ModelAdmin):
    list_display = [ 'name', 'data' ]

admin.site.register(BindServer)
admin.site.register(Key, KeyAdmin)
