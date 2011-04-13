from django.db import models

import dns.query
import dns.zone

class BindServer(models.Model):
    hostname = models.CharField(max_length=100)

    def __unicode__(self):
        return self.hostname

class Key(models.Model):
    name = models.CharField(max_length=50)
    data = models.CharField(max_length=24)

    def __unicode__(self):
        return self.name
    
class Zone(models.Model):
    server = models.ForeignKey('BindServer')
    zone_name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.zone_name
