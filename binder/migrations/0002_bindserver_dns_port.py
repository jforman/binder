# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('binder', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bindserver',
            name='dns_port',
            field=models.IntegerField(default=53, verbose_name='DNS port', help_text=b'The port where the BIND server is listening for DNSrequests. binder especially uses that port for the dynamic zone updates. In most cases you should always leave it at the default port 53.'),
            preserve_default=True,
        ),
    ]
