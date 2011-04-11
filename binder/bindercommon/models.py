from django.db import models

class BindServer(models.Model):
    name = models.CharField(max_length=50)
    hostname = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

class Key(models.Model):
    name = models.CharField(max_length=50)
    data = models.TextField()

    def __unicode__(self):
        return self.name
    
class Zone(models.Model):
    server = models.ForeignKey('BindServer')
    key = models.ForeignKey('Key')
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return "%s: %s" % (self.server, self.name)
