from django.test import TestCase

from binder import models, helpers

class HelperTests(TestCase):
    def test_ipinfo_ResolutionFail(self):
        response = helpers.ip_info("foobar.doesnotexist.local")
        self.assertEqual([['Error', u'Unable to resolve foobar.doesnotexist.local: [Errno -2] Name or service not known']],
                         response)
        # The following is currently the first globally unique IPv4 and IPv6 address I could find
        # that did not change based upon your geography.
        # http://test-ipv6.com/
        response = helpers.ip_info("ds.test-ipv6.com")
        self.assertEqual([['IPv4 (1)', u'216.218.228.114'], ['IPv6 (1)', u'2001:470:1:18::2']],
                         response)

