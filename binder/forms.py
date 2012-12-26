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

class CustomStringPeriodSuffix(forms.CharField):
    """ Convert unicode to string and make sure period is last character. """
    ### This seems very unclean. Need a better to way to complete the fqdn
    ###  depending on if it ends in a period.
    ### TODO(jforman): Add Regex check in here for valid rr data
    ###  http://www.zytrax.com/books/dns/apa/names.html
    def clean(self, value):
        try:
            new_string = str(value)
            if new_string[-1] != ".":
                new_string += "."
        except:
            raise ValidationError("Unable to stick a period on the end of your input: %r" % value)

        return new_string
### Form Models

class FormAddForwardRecord(forms.Form):
    """ Form used to add a Forward DNS record. """
    dns_server = forms.CharField(max_length=100)
    record_name = forms.RegexField(max_length=100, regex="^[a-zA-Z0-9-_]+$", required=False)
    record_type = forms.ChoiceField(choices=local_settings.RECORD_TYPE_CHOICES)
    zone_name = forms.CharField(max_length=100)
    record_data = forms.GenericIPAddressField()
    ttl = forms.ChoiceField(choices=local_settings.TTL_CHOICES)
    create_reverse = forms.BooleanField(required=False)
    key_name = forms.ModelChoiceField(queryset=Key.objects.all(), required=False)

class FormAddReverseRecord(forms.Form):
    """ Form used to add a Reverse (PTR) DNS record. """
    dns_server = forms.CharField(max_length=100)
    record_name = forms.IntegerField(min_value=0, max_value=255)
    record_type = forms.RegexField(regex=r"^PTR$",error_messages={"invalid" : "The only valid choice here is PTR."})
    zone_name = forms.CharField(max_length=100)
    record_data = CustomStringPeriodSuffix(required=True)
    ttl = forms.ChoiceField(choices=local_settings.TTL_CHOICES)
    key_name = forms.ModelChoiceField(queryset=Key.objects.all(), required=False)
    create_reverse = forms.BooleanField(required=False)

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
