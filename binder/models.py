### Binder Models

# Standard Imports
import binascii
import socket

# 3rd Party
from cryptography.fernet import Fernet, InvalidToken
from pybindxml import reader as bindreader
import dns.exception
import dns.query
import dns.tsig
import dns.zone

# App Imports
from binder import exceptions
from django.db import models
from django.conf import settings

TSIG_ALGORITHMS = (('HMAC-MD5.SIG-ALG.REG.INT', 'MD5'),
                   ('hmac-sha1', 'SHA1'),
                   ('hmac-sha256', 'SHA256'),
                   ('hmac-sha384', 'SHA384'),
                   ('hmac-sha512', 'SHA512'))


class Key(models.Model):

    """Store and reference TSIG keys."""

    name = models.CharField(max_length=255,
                            unique=True,
                            help_text="A human readable name for the key to "
                            "store, used for further references to the key.")
    data = models.CharField(max_length=255,
                            help_text="The private part of the TSIG key.")
    algorithm = models.CharField(max_length=255,
                                 choices=TSIG_ALGORITHMS,
                                 help_text="The algorithm which has been used "
                                 "for the key.")

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]


    def save(self, *args, **kwargs):
        f = Fernet(settings.FERNET_KEY)
        crypted_key = f.encrypt(bytes(self.data))
        self.data = crypted_key
        super(Key, self).save(*args, **kwargs)

    def create_keyring(self):
        if self.name is None:
            return None

        try:
            key_data = self.decrypt_keydata()
            keyring = dns.tsigkeyring.from_text({self.name: key_data})
        except binascii.Error, err:
            raise exceptions.KeyringException("Incorrect key data. Verify key: %s. Reason: %s" % (self.name, err))

        return keyring

    def decrypt_keydata(self, key=None):
        if key:
            fernet_key=key
        else:
            fernet_key=settings.FERNET_KEY
        try:
            f = Fernet(fernet_key)
            decrypted_key = f.decrypt(bytes(self.data))
        except InvalidToken:
            raise exceptions.KeyringException()

        return decrypted_key


class BindServer(models.Model):

    """Store DNS servers and attributes for referencing their statistics ports.

    Also reference FK for TSIG transfer keys, if required.
    """

    hostname = models.CharField(max_length=255,
                                unique=True,
                                help_text="Host name or IP address of the BIND server.")
    dns_port = models.IntegerField(default=53,
                                   verbose_name="DNS port",
                                   help_text="The port where the BIND server is listening for DNS "
                                   "requests. binder especially uses that port for the dynamic "
                                   "zone updates. In most cases you should always leave it at the "
                                   "default port 53.")
    statistics_port = models.IntegerField(help_text="Port where the BIND server is serving "
                                          "statistics on.")
    default_transfer_key = models.ForeignKey(Key,
                                             null=True,
                                             blank=True,
                                             help_text="The default key to use for all actions "
                                             "with this DNS server as long as no other key is "
                                             "specified explicitly.")

    def __unicode__(self):
        return self.hostname

    class Meta:
        ordering = ["hostname"]

    def list_zones(self):
        """List the DNS zones and attributes.

        TODO: Parse these XML more intelligently. Grab the view name. Any other data available?

        Returns:
          List of Dicts { String view_name,
                          String zone_name,
                          String zone_class,
                          String zone_serial }
        """
        zone_data = bindreader.BindXmlReader(host=self.hostname, port=self.statistics_port)
        zone_data.get_stats()
        return zone_data

    def list_zone_records(self, zone_name):
        """List all records in a specific zone.

        TODO: Print out current_record in the loop and see if we can parse this more programatically,
              rather than just splitting on space. What is the difference between class and type?
        Arguments:
          String zone_name: Name of the zone

        Returns:
          List of Dicts { String rr_name, String rr_ttl, String rr_class, String rr_type, String rr_data }
        """
        try:
            transfer_key = Key.objects.get(name=self.default_transfer_key)
        except Key.DoesNotExist:
            keyring = None
            algorithm = None
        else:
            keyring = transfer_key.create_keyring()
            algorithm = transfer_key.algorithm

        try:
            zone = dns.zone.from_xfr(dns.query.xfr(self.hostname,
                                                   zone_name,
                                                   port=self.dns_port,
                                                   keyring=keyring,
                                                   keyalgorithm=algorithm))
        except dns.tsig.PeerBadKey:
            # The incorrect TSIG key was selected for transfers.
            raise exceptions.TransferException("Unable to list zone records because of a TSIG key mismatch.")
        except socket.error, err:
            # Thrown when the DNS server does not respond for a zone transfer (XFR).
            raise exceptions.TransferException("DNS server did not respond for transfer. Reason: %s" % err)
        except dns.exception.FormError:
            # When the DNS message is malformed.
            # * Can happen if a TSIG key is required but a default_transfer_key is not specified.
            raise exceptions.TransferException("Unable to perform AXFR to list zone records. Did you forget to specify a default transfer key?")

        names = zone.nodes.keys()
        names.sort()
        record_array = []
        for current_name in names:
            current_record = zone[current_name].to_text(current_name)
            for split_record in current_record.split("\n"):
                current_record = split_record.split(" ")
                rr_dict = {}
                rr_dict["rr_name"] = current_record[0]
                rr_dict["rr_ttl"] = current_record[1]
                rr_dict["rr_class"] = current_record[2]
                rr_dict["rr_type"] = current_record[3]
                rr_dict["rr_data"] = current_record[4]

                record_array.append(rr_dict)

        return record_array
