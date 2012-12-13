from django.test import TestCase

from binder import forms

class Form_Tests(TestCase):
    def test_Valid_FormAddRecord(self):
        """Test FormAddRecord with valid data, with/without create_reverse."""
        form_data = {"dns_server":"server1",
                     "record_name":"record1",
                     "record_type":"A",
                     "zone_name":"domain.local",
                     "record_data":"10.254.254.254",
                     "ttl":3600,
                     "key_name": None,
                     "create_reverse" : False}

        testform_1 = forms.FormAddRecord(form_data)
        self.assertTrue(testform_1.is_valid())

        form_data = {"dns_server":"server1",
                     "record_name":"record1",
                     "record_type":"A",
                     "zone_name":"domain.local",
                     "record_data":"10.254.254.254",
                     "ttl":3600,
                     "key_name":None,
                     "create_reverse":True}

        testform_2 = forms.FormAddRecord(form_data)
        self.assertTrue(testform_2.is_valid())


    def test_MissingData_FormAddRecord(self):
        """ Submit FormAddRecord with missing record_data."""
        form_data = {"dns_server":"server1",
                     "record_name":"record1",
                     "record_type": "A",
                     "zone_name":"domain.local",
                     "record_data":"",
                     "ttl": 300,
                     "key_name":None,
                     "create_reverse":True}

        expected_form_errors = {"record_data": [u"This field is required."]}
        testform = forms.FormAddRecord(form_data)
        testform.is_valid()
        self.assertFalse(testform.is_valid())
        self.assertEquals(expected_form_errors, testform.errors)

    def test_InvalidValue_FormAddRecord(self):
        """ Pass FormAddRecord invalid values, compare error response dicts."""
        form_data = {"dns_server":"server1",
                     "record_name":"record1$$$",
                     "record_type":123,
                     "zone_name":"domain.local",
                     "record_data":"A.B.C.D",
                     "ttl":"A",
                     "key_name":None,
                     "create_reverse":True}

        expected_form_errors = {"record_data": [u"Enter a valid IPv4 or IPv6 address."],
                                "record_name": [u"Enter a valid value."],
                                "record_type": [u"Select a valid choice. 123 is not one of the available choices."],
                                "ttl": [u'Select a valid choice. A is not one of the available choices.']}
        testform_2 = forms.FormAddRecord(form_data)
        testform_2.is_valid()
        self.assertFalse(testform_2.is_valid())
        self.assertEquals(expected_form_errors, testform_2.errors)

    def test_Validation_FormDeleteRecord(self):
        """Validate good data in the FormDeleteRecord form."""
        delete_dict = { "dns_server" : "foo.net",
                        "zone_name" : "domain1.local",
                        "rr_list" : '[u"record1.domain1.local", u"record2.domain1.local"]',
                        }
        testform_1 = forms.FormDeleteRecord(delete_dict)
        testform_1.is_valid
        self.assertFalse(testform_1.errors)
        delete_dict["rr_list"] = '[record1.domain1.local", u"record2.domain1.local"]'
        testform_1 = forms.FormDeleteRecord(delete_dict)
        testform_1.is_valid
        self.assertTrue(testform_1.errors)

    def test_MissingName_AddCnameForm(self):
        """Attempt to submit a cname add form missing the cname value."""
        form_dict = { "dns_server" : "testserver1",
                      "zone_name" : "domain1.local",
                      "originating_record" : "record1.domain1.local",
                      "cname" : "",
                      "ttl" : 300 }
        expected_form_errors = { "cname" : [u"This field is required."] }
        testform_1 = forms.FormAddCnameRecord(form_dict)
        testform_1.is_valid()
        self.assertTrue(testform_1.errors)
        self.assertEquals(testform_1.errors, expected_form_errors)
