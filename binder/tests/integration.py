from django.test import TestCase
from django.test.client import Client

from binder import helpers, models

class Integration_Tests(TestCase):
    fixtures = [ "binder/fixtures/binder_test.json" ]

    def setUp(self):
        self.client = Client()
        self.testserver = models.BindServer.objects.get(hostname="testserver1").hostname

    def test_Integration_Add_Record(self):
        """Add forward and reverse record on domain1.local."""
        add_dict = { "dns_server" : self.testserver,
                     "record_name" : "record1",
                     "record_type" : "A",
                     "zone_name" : "domain1.local",
                     "record_data" : "10.254.1.101",
                     "ttl" : 86400,
                     "create_reverse" : True}
        response = self.client.post("/add_record/result/", add_dict)
        self.assertEqual(response.status_code, 200)
        # Make sure that we get two responses (fwd/rev) back from the server.
        self.assertEqual(len(response.context["response"]), 2)

        for current_response in response.context["response"]:
            dns_update_output = str(current_response["output"])
            self.assertRegexpMatches(dns_update_output, "opcode UPDATE")
            self.assertRegexpMatches(dns_update_output, "rcode NOERROR")

    def test_Integration_Delete_Record(self):
        """Delete record1.domain1.local"""
        delete_dict = { "dns_server" : self.testserver,
                        "zone_name" : "domain1.local",
                        "rr_list" : '[u"record1.domain1.local", u"record2.domain1.local"]',
                     }
        response = self.client.post("/delete_record/result/", delete_dict)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["response"]), 2)
        for current_response in response.context["response"]:
            dns_update_output = str(current_response["output"])
            self.assertRegexpMatches(dns_update_output, "opcode UPDATE")
            self.assertRegexpMatches(dns_update_output, "rcode NOERROR")

    
    def test_Integration_Add_Cname(self):
        """ Add CNAME cnametest1 after adding associated A record record1."""
        add_dict = { "dns_server" : self.testserver,
                     "record_name" : "record1",
                     "record_type" : "A",
                     "zone_name" : "domain1.local",
                     "record_data" : "10.254.1.101",
                     "ttl" : 86400,
                     "create_reverse" : False}
        response = self.client.post("/add_record/result/", add_dict)
        self.assertEqual(response.status_code, 200)
        # Make sure that we get two responses (fwd/rev) back from the server.
        self.assertEqual(len(response.context["response"]), 1)

        for current_response in response.context["response"]:
            dns_update_output = str(current_response["output"])
            self.assertRegexpMatches(dns_update_output, "opcode UPDATE")
            self.assertRegexpMatches(dns_update_output, "rcode NOERROR")

        cname_dict = { "dns_server" : self.testserver,
                       "originating_record" : "record1.domain1.local",
                       "cname" : "cnametest1",
                       "zone_name" : "domain1.local",
                       "ttl" : 86400,
                       }
        response = self.client.post("/add_cname_record/result/", cname_dict)
        self.assertEqual(response.status_code, 200)
        for current_response in response.context["response"]:
            dns_update_output = str(current_response["output"])
            self.assertRegexpMatches(dns_update_output, "opcode UPDATE")
            self.assertRegexpMatches(dns_update_output, "rcode NOERROR")
                       
