from django import forms

from bcommon.models import BindServer, Key

RECORD_TYPE_CHOICES = (("A", "A"), ("AAAA", "AAAA"), ("CNAME", "CNAME"))
TTL_CHOICES = ((300, "5 minutes"),
               (1800, "30 minutes"),
               (3600, "1 hour"),
               (43200, "12 hours"),
               (86400, "1 day"))

class FormAddRecord(forms.Form):
    dns_server = forms.CharField(max_length=100, label="Hostname of DNS Server", widget=forms.TextInput(attrs={'readonly':'readonly'}))
    name = forms.CharField(max_length=100, label="Record Name (FQDN)")
    record_type = forms.ChoiceField(choices=RECORD_TYPE_CHOICES, label="Record Type")
    ttl = forms.ChoiceField(choices=TTL_CHOICES, label="TTL", initial=86400)
    create_reverse = forms.BooleanField(label="Create Reverse Record (PTR)?", required=False)
    data = forms.CharField(max_length=256, label="Record Data (IP/Hostname)")
    key_name = forms.ModelChoiceField(queryset=Key.objects.all(), empty_label=None, label="TSIG Key")
