from django.db import models

import dns.query
import dns.zone

TSIG_ALGORITHMS = (('hmac-md5', 'MD5'),('hmac-sha1', 'SHA1'),('hmac-224', 'SHA224'),('hmac-sha256', 'SHA256'),('hmac-sha384', 'SHA384'),('hmac-sha512', 'SHA512'))

class BindServer(models.Model):
    hostname = models.CharField(max_length=100)

    def __unicode__(self):
        return self.hostname

class Key(models.Model):
    name = models.CharField(max_length=50)
    data = models.CharField(max_length=150)
    algorithm = models.CharField(max_length=12, choices=TSIG_ALGORITHMS)

    def __unicode__(self):
        return self.name
