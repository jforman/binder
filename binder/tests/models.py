from django.test import TestCase

from binder import models

class ModelTests(TestCase):
    def test_EmptyBindServerModel(self):
        self.assertEqual(models.BindServer.objects.count(), 0)
        bindserver_1 = models.BindServer(hostname="test1",
                                        statistics_port = 1234)
        bindserver_1.save()
        self.assertEqual(models.BindServer.objects.count(), 1)
