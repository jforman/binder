### Binder Forms

# 3rd Party
from django import forms
from django.core.exceptions import ValidationError

# App Imports
from models import Key
import local_settings

### Custom Form Fields

class CustomUnicodeListField(forms.CharField):
    """ Convert unicode item list to list of strings. """
    def clean(self, value):
        try:
            first_parse = eval(value)
            string_list = [current_item for current_item in first_parse]
        except:
            raise ValidationError("Error in converting Unicode list to list of Strings: %r" % value)

        return string_list

### Form Models

class FormAddRecord(forms.Form):
    """ Form used to add a DNS record. """
    dns_server = forms.CharField(max_length=100)
    record_name = forms.RegexField(max_length=100, regex="^[a-zA-Z0-9-_]+$", required=False)
    record_type = forms.ChoiceField(choices=local_settings.RECORD_TYPE_CHOICES)
    zone_name = forms.CharField(max_length=100)
    record_data = forms.GenericIPAddressField()
    ttl = forms.ChoiceField(choices=local_settings.TTL_CHOICES)
    create_reverse = forms.BooleanField(required=False)
    key_name = forms.ModelChoiceField(queryset=Key.objects.all(), required=False)


class FormAddCnameRecord(forms.Form):
    """ Form used to add a CNAME record. """
    dns_server = forms.CharField(max_length=100)
    originating_record = forms.CharField(max_length=100)
    cname = forms.RegexField(max_length=100, regex="^[a-zA-Z0-9-_]+$")
    zone_name = forms.CharField(max_length=256)
    ttl = forms.ChoiceField(choices=local_settings.TTL_CHOICES)
    key_name = forms.ModelChoiceField(queryset=Key.objects.all(), required=False)

class FormDeleteRecord(forms.Form):
    """ Final form to delete DNS record(s). """
    dns_server = forms.CharField(max_length=100)
    zone_name = forms.CharField(max_length=256)
    rr_list = CustomUnicodeListField(required=False)
    key_name = forms.ModelChoiceField(queryset=Key.objects.all(), required=False)
