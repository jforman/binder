# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BindServer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hostname', models.CharField(help_text=b'Host name or IP address of the BIND server.', unique=True, max_length=255)),
                ('statistics_port', models.IntegerField(help_text=b'Port where the BIND server is serving statistics on.')),
            ],
            options={
                'ordering': ['hostname'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Key',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'A human readable name for the key to store, used for further references to the key.', unique=True, max_length=255)),
                ('data', models.CharField(help_text=b'The private part of the TSIG key.', max_length=255)),
                ('algorithm', models.CharField(help_text=b'The algorithm which has been used for the key.', max_length=255, choices=[(b'HMAC-MD5.SIG-ALG.REG.INT', b'MD5'), (b'hmac-sha1', b'SHA1'), (b'hmac-sha256', b'SHA256'), (b'hmac-sha384', b'SHA384'), (b'hmac-sha512', b'SHA512')])),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='bindserver',
            name='default_transfer_key',
            field=models.ForeignKey(blank=True, to='binder.Key', help_text=b'The default key to use for all actions with this DNS server as long as no other key is specified explicitly.', null=True),
            preserve_default=True,
        ),
    ]
