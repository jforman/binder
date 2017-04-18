# Binder Forms

# 3rd Party
from django import forms
from django.conf import settings
from django.contrib import messages
from django.core import validators
from django.forms import ValidationError

# App Imports
from models import Key


class CustomUnicodeListField(forms.CharField):

    """Convert unicode item list to list of strings."""

    def clean(self, value):
        try:
            string_list = [str(cur_rr) for cur_rr in eval(value)]
        except:
            raise ValidationError("Error in converting Unicode list to list "
                                  "of strings: %r" % value)
        return string_list


class CustomStringPeriodSuffix(forms.CharField):

    """Convert unicode to string and make sure period is last character.

    This seems very unclean. Need a better to way to complete the fqdn
    depending on if it ends in a period.
    TODO(jforman): Add Regex check in here for valid rr data
    http://www.zytrax.com/books/dns/apa/names.html
    """

    def clean(self, value):
        try:
            new_string = str(value)
            if new_string[-1] != ".":
                new_string += "."
        except:
            raise ValidationError("Unable to stick a period on the end of "
                                  "your input: %r" % value)

        return new_string


class FormAddForwardRecord(forms.Form):

    """Form used to add a Forward DNS record."""

    dns_server = forms.CharField(max_length=100)
    record_name = forms.RegexField(max_length=100,
                                   regex="^[a-zA-Z0-9-_]+$",
                                   required=False)
    record_type = forms.ChoiceField(choices=settings.RECORD_TYPE_CHOICES)
    zone_name = forms.CharField(max_length=100)
    record_data = forms.CharField(max_length=100)
    ttl = forms.ChoiceField(choices=settings.TTL_CHOICES)
    create_reverse = forms.BooleanField(required=False)
    key_name = forms.ModelChoiceField(queryset=Key.objects.all(), required=True)

    def clean(self):
        cleaned_data = super(FormAddForwardRecord, self).clean()
        record_type = cleaned_data.get("record_type")
        record_data = cleaned_data.get("record_data")
        if record_type in ("A", "AAAA"):
            try:
                validators.validate_ipv46_address(record_data)
            except:
                raise ValidationError("Invalid IP Address.")

class FormAddReverseRecord(forms.Form):

    """Form used to add a Reverse (PTR) DNS record."""

    dns_server = forms.CharField(max_length=100)
    record_name = forms.IntegerField(min_value=0, max_value=255)
    record_type = forms.RegexField(regex=r"^PTR$",
                                   error_messages={
                                       "invalid": "The only valid choice here "
                                                  "is PTR."})
    zone_name = forms.CharField(max_length=100)
    record_data = CustomStringPeriodSuffix(required=True)
    ttl = forms.ChoiceField(choices=settings.TTL_CHOICES)
    create_reverse = forms.BooleanField(required=False)
    key_name = forms.ModelChoiceField(queryset=Key.objects.all(), required=True)


class FormAddCnameRecord(forms.Form):

    """Form used to add a CNAME record."""

    dns_server = forms.CharField(max_length=100)
    originating_record = forms.CharField(max_length=100)
    cname = forms.RegexField(max_length=100, regex="^[a-zA-Z0-9-_]+$")
    zone_name = forms.CharField(max_length=256)
    ttl = forms.ChoiceField(choices=settings.TTL_CHOICES)
    key_name = forms.ModelChoiceField(queryset=Key.objects.all(), required=True)


class FormDeleteRecord(forms.Form):

    """Final form to delete DNS record(s)."""

    dns_server = forms.CharField(max_length=100)
    zone_name = forms.CharField(max_length=256)
    rr_list = CustomUnicodeListField()
    key_name = forms.ModelChoiceField(queryset=Key.objects.all(), required=True)
