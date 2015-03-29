from django.test import TestCase

from binder import models, helpers

class HelperTests(TestCase):
    def test_ipinfo_ResolutionFail(self):
        response = helpers.ip_info("foobar.doesnotexist.local")
        self.assertEqual([['Error', u'Unable to resolve foobar.doesnotexist.local: [Errno -2] Name or service not known']],
                         response)
        response = helpers.ip_info("localhost")
        self.assertEqual([['IPv4 (1)', u'127.0.0.1'], ['IPv6 (1)', u'::1']],
                         sorted(response))
