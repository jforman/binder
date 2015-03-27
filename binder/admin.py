import binascii
import dns.tsigkeyring
from models import BindServer, Key
from django.contrib import admin
from django.forms import ModelForm, ValidationError

class BindServerAdminForm(ModelForm):
    def clean_statistics_port(self):
        port = self.cleaned_data["statistics_port"]
        if port < 1 or port > 65535:
            raise ValidationError("Invalid port number %(port)s. Please enter "
                                  "a valid one between 1 and 65535.",
                                  params={'port': port})
        return self.cleaned_data["statistics_port"]


    def clean_dns_port(self):
        port = self.cleaned_data["dns_port"]
        if port < 1 or port > 65535:
            raise ValidationError("Invalid port number %(port)s. Please enter "
                                  "a valid one between 1 and 65535.",
                                  params={'port': port})
        return self.cleaned_data["dns_port"]


class BindServerAdmin(admin.ModelAdmin):
    form = BindServerAdminForm
    list_display = ['hostname', 'statistics_port', 'default_transfer_key']


class KeyAdminForm(ModelForm):
    def clean_data(self):
        try:
            keyring = dns.tsigkeyring.from_text({'': self.cleaned_data["data"]})
        except binascii.Error as err:
            raise ValidationError("Invalid key data: %(error)s",
                                  params={'error': err})
        return self.cleaned_data["data"]


class KeyAdmin(admin.ModelAdmin):
    form = KeyAdminForm
    list_display = ['name', 'data', 'algorithm']


admin.site.register(BindServer, BindServerAdmin)
admin.site.register(Key, KeyAdmin)
