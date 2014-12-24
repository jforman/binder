from django.test import TestCase
from django.db import IntegrityError

from binder import models

class Model_BindServer_Tests(TestCase):
    def test_BindServerModel(self):
        """Test that adding a well-formed BindServer works."""
        self.assertEqual(models.BindServer.objects.count(), 0)
        bindserver_1 = models.BindServer(hostname="test1",
                                         statistics_port=1234)
        bindserver_1.save()
        self.assertEqual(models.BindServer.objects.count(), 1)

    def test_BindServerMissingStatisticsPort(self):
        """Attempt to add a BindServer without a statistics port."""
        bindserver_1 = models.BindServer(hostname="badtest1")
        with self.assertRaisesMessage(IntegrityError, "NOT NULL constraint failed: binder_bindserver.statistics_port"):
            bindserver_1.save()

    def test_BindServerNonIntStatisticsPort(self):
        """Attempt to add a Bindserver with a non-integer statistics port."""
        bindserver_1 = models.BindServer(hostname="foo",
                                         statistics_port="bar1")
        with self.assertRaisesMessage(ValueError, "invalid literal for int() with base 10: 'bar1'"):
            bindserver_1.save()


class Model_Key_Tests(TestCase):
    def test_KeyModel(self):
        """ Test that adding a well-formed Key works."""
        self.assertEqual(models.Key.objects.count(), 0)
        key_1 = models.Key(name="testkey1",
                           data="abc123",
                           algorithm="MD5")
        key_1.save()
        self.assertEqual(models.Key.objects.count(), 1)

    def test_NonExistantKey(self):
        with self.assertRaisesMessage(models.Key.DoesNotExist, "Key matching query does not exist"):
            this_key = models.Key.objects.get(name="does_not_exist")
