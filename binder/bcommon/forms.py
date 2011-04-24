from django import forms

from bcommon.models import BindServer, Key

class FormAddRecord(forms.Form):
    dns_hostname = forms.CharField(max_length=100)
    rr_domain = forms.CharField(max_length=100)
    rr_name = forms.CharField(max_length=256)
    rr_type = forms.ChoiceField(choices=(("A", "A"), ("MX", "MX"), ("CNAME", "CNAME"), ("AAAA", "AAAA")))
    rr_data = forms.CharField(max_length=256)
    tsig_key = forms.ModelChoiceField(queryset=Key.objects.all(), empty_label=None)
