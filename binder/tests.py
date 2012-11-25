from django.test import TestCase
from django.test.client import Client

from binder import models

class GetTests(TestCase):
    """ Unit Tests that exercise HTTP GET. """
    def setUp(self):
        self.client = Client()

    def test_GetIndex(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_GetServerIndex(self):
        response = self.client.get("/server_list/")
        self.assertEqual(response.status_code, 200)

    def test_GetResultRedirects(self):
        """ Expected Output: Redirect to / """
        response = self.client.get("/add_record/result/", follow=True)
        self.assertRedirects(response, "/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/delete_record/result/", follow=True)
        self.assertRedirects(response, "/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/add_cname_record/result/", follow=True)
        self.assertRedirects(response, "/")
        self.assertEqual(response.status_code, 200)

    def test_GetInvalidServer(self):
        """ Attempt to get a zone list for a server
        not configured in the database. 
        """
        response = self.client.get("/info/unconfigured.server.net/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ('<div class="alert alert-error">Errors were encountered: <br>'
                                       'There is no configured server by that name: unconfigured.server.net </div>'),
                            html=True)


class ModelTests(TestCase):
    def test_EmptyBindServerModel(self):
        self.assertEqual(models.BindServer.objects.count(), 0)
        bindserver_1 = models.BindServer(hostname="test1",
                                        statistics_port = 1234)
        bindserver_1.save()
        self.assertEqual(models.BindServer.objects.count(), 1)


class PostTests(TestCase):
    """ Unit Tests that exercise HTTP POST. """
    def setUp(self):
        self.client = Client()

    def test_DeleteRecordInitial_Empty(self):
        """ Ensure the initial deletion form works as expected with no RR list. """
        response = self.client.post("/delete_record/", { "dns_server" : "testserver.test.net",
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
        response = self.client.post("/delete_record/", { "dns_server" : "testserver.test.net",
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

