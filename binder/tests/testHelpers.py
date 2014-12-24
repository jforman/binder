from django.test import TestCase

from binder import models, helpers

class HelperTests(TestCase):
    def test_ipinfo_ResolutionFail(self):
        response = helpers.ip_info("foobar.doesnotexist.local")
        self.assertEqual([['Error', u'Unable to resolve foobar.doesnotexist.local: [Errno -2] Name or service not known']],
                         response)
        response = helpers.ip_info("time1.google.com")
        self.assertEqual([['IPv4 (1)', u'216.239.32.15'], ['IPv6 (1)', u'2001:4860:4802:32::f']],
                         response)

