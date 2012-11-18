from django import forms
from models import Key

RECORD_TYPE_CHOICES = (("A", "A"), ("AAAA", "AAAA"), ("CNAME", "CNAME"))
TTL_CHOICES = ((300, "5 minutes"),
               (1800, "30 minutes"),
               (3600, "1 hour"),
               (43200, "12 hours"),
               (86400, "1 day"))

class FormAddRecord(forms.Form):
    dns_server = forms.CharField(max_length=100)
    record_name = forms.RegexField(max_length=100, regex="^[a-zA-Z0-9-_]+$", required=False)
    record_type = forms.CharField(max_length=10)
    zone_name = forms.CharField(max_length=100)
    record_data = forms.GenericIPAddressField()
    ttl = forms.IntegerField(min_value=1)
    create_reverse = forms.BooleanField(required=False)
    key_name = forms.ModelChoiceField(queryset=Key.objects.all(), required=False)


class FormAddCnameRecord(forms.Form):
    dns_server = forms.CharField(max_length=100)
    originating_record = forms.CharField(max_length=100)
    cname = forms.RegexField(max_length=100, regex="^[a-zA-Z0-9-_]+$")
    zone_name = forms.CharField(max_length=256)
    ttl = forms.ChoiceField(choices=TTL_CHOICES)
    key_name = forms.ModelChoiceField(queryset=Key.objects.all(), required=False)
