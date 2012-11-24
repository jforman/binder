from django import forms
from models import Key

TTL_CHOICES = ((300, "5 minutes"),
               (1800, "30 minutes"),
               (3600, "1 hour"),
               (43200, "12 hours"),
               (86400, "1 day"))

RECORD_TYPE_CHOICES = (("A", "A"), ("AAAA", "AAAA"), ("CNAME", "CNAME"))

### Custom Form Fields

class CustomUnicodeListField(forms.CharField):
    """ Convert unicode item list to list of strings. """
    def clean(self, value):
        try:
            first_parse = eval(value)
            string_list = [current_item for current_item in first_parse]
        except:
            raise ValidationError

        return string_list

### Form Models

class FormAddRecord(forms.Form):
    """ Form used to add a DNS record. """
    dns_server = forms.CharField(max_length=100)
    record_name = forms.RegexField(max_length=100, regex="^[a-zA-Z0-9-_]+$", required=False)
    record_type = forms.CharField(max_length=10)
    zone_name = forms.CharField(max_length=100)
    record_data = forms.GenericIPAddressField()
    ttl = forms.IntegerField(min_value=1)
    create_reverse = forms.BooleanField(required=False)
    key_name = forms.ModelChoiceField(queryset=Key.objects.all(), required=False)


class FormAddCnameRecord(forms.Form):
    """ Form used to add a CNAME record. """
    dns_server = forms.CharField(max_length=100)
    originating_record = forms.CharField(max_length=100)
    cname = forms.RegexField(max_length=100, regex="^[a-zA-Z0-9-_]+$")
    zone_name = forms.CharField(max_length=256)
    ttl = forms.ChoiceField(choices=TTL_CHOICES)
    key_name = forms.ModelChoiceField(queryset=Key.objects.all(), required=False)

class FormDeleteRecord(forms.Form):
    """ Final form to delete DNS record(s). """
    dns_server = forms.CharField(max_length=100)
    zone_name = forms.CharField(max_length=256)
    rr_list = CustomUnicodeListField(required=False)
    key_name = forms.ModelChoiceField(queryset=Key.objects.all(), required=False)
