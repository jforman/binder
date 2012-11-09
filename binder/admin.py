from models import BindServer, Key
from django.contrib import admin

class BindServerAdmin(admin.ModelAdmin):
    list_display = [ 'hostname',  'statistics_port', 'default_transfer_key' ]

class KeyAdmin(admin.ModelAdmin):
    list_display = [ 'name', 'data', 'algorithm' ]

admin.site.register(BindServer, BindServerAdmin)
admin.site.register(Key, KeyAdmin)
