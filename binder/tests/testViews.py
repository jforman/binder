from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from binder import models, helpers


class GetTests(TestCase):
    """ Unit Tests that exercise HTTP GET. """
    def setUp(self):
        self.client = Client()

    def test_GetIndex(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_GetServerIndex(self):
        response = self.client.get(reverse("server_list"))
        self.assertEqual(response.status_code, 200)

    def test_GetResultRedirects(self):
        """ GETing a /result/ URL should always redirect to /. """
        response = self.client.get(reverse("add_record_result"), follow=True)
        self.assertRedirects(response, reverse("index"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("delete_record_result"), follow=True)
        self.assertRedirects(response, reverse("index"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("add_cname_result"), follow=True)
        self.assertRedirects(response, reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_GetInvalidServer(self):
        """ Get a zone list for a server not in the database."""
        server_name = "unconfigured.server.net"
        response = self.client.get(reverse("server_zone_list", args=(server_name, )))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ('<div class="alert alert-error">Errors were encountered: <br>'
                                       'There is no configured server by that name: unconfigured.server.net </div>'),
                            html=True)


class PostTests(TestCase):
    """ Unit Tests that exercise HTTP POST. """
    def setUp(self):
        self.client = Client()

    def test_DeleteRecordInitial_Empty(self):
        """ Ensure the initial deletion form works as expected with no RR list. """
        response = self.client.post(reverse("delete_record"), { "dns_server" : "testserver.test.net",
                                                                "zone_name" : "testzone1.test.net",
                                                                "rr_list" : [] })

        self.assertContains(response,
                            '<input type="hidden" name="zone_name" value="testzone1.test.net">',
                            html=True)
        self.assertContains(response,
                            '<input type="hidden" name="rr_list" value="[]">',
                            html=True)
        self.assertContains(response,
                            '<input type="hidden" name="dns_server" value="testserver.test.net" />',
                            html=True)


    def test_DeleteRecordInitial(self):
        """ Ensure the initial deletion form works as expected with RRs mentioned. """
        response = self.client.post(reverse("delete_record"), {"dns_server" : "testserver.test.net",
                                                               "zone_name" : "testzone1.test.net",
                                                               "rr_list" : ["testrecord1.testzone1.test.net",
                                                                            "testrecord2.testzone1.test.net"] })

        self.assertContains(response,
                            '<input type="hidden" name="zone_name" value="testzone1.test.net">',
                            html=True)
        self.assertContains(response,
                            '<input type="hidden" name="rr_list" value="[u\'testrecord1.testzone1.test.net\', u\'testrecord2.testzone1.test.net\']">',
                            html=True)
        self.assertContains(response,
                            '<input type="hidden" name="dns_server" value="testserver.test.net" />',
                            html=True)
