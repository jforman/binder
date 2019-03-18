import binascii
import dns.tsigkeyring
from binder.models import BindServer, Key
from django.contrib import admin
from django.forms import ModelForm, ValidationError


class BindServerAdmin(admin.ModelAdmin):
    list_display = ['hostname', 'server_type', 'control_port', 'default_transfer_key']


class KeyAdminForm(ModelForm):
    def clean_data(self):
        try:
            dns.tsigkeyring.from_text({'': self.cleaned_data["data"]})
        except binascii.Error as err:
            raise ValidationError("Invalid key data: %(error)s",
                                  params={'error': err})
        return self.cleaned_data["data"]


class KeyAdmin(admin.ModelAdmin):
    form = KeyAdminForm
    list_display = ['name', 'data', 'algorithm']


admin.site.register(BindServer, BindServerAdmin)
admin.site.register(Key, KeyAdmin)
