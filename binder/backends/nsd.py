# NSD Backend Handler Class

import os
from django.conf import settings
from jinja2 import Template
import re
import subprocess

NSD_CONF_TEMPLATE = """
# nsd.conf for {{hostname}}
remote-control:
    control-enable: yes
    control-key-file: {{creds_dir}}/{{hostname}}/nsd_control.key
    control-cert-file: {{creds_dir}}/{{hostname}}/nsd_control.pem
    server-cert-file: {{creds_dir}}/{{hostname}}/nsd_server.pem

"""

ZONE_RE = re.compile("""
zone\:\s+(?P<zone_name>\S+)
\s+state: master""")

class NSDServer(object):
    """Class to manage NSD backend server data."""

    def __init__(self, hostname, control_port):
        self.hostname = hostname
        self.control_port = control_port

    def get_creds_dir(self):
        return os.path.join(settings.CREDS_DIR,
                            self.hostname)


    def get_config_path(self):
        return os.path.join(
            os.path.join(self.get_creds_dir()),
            'nsd.conf')

    def write_config(self):
        if not os.path.exists(self.get_creds_dir()):
            os.makedirs(self.get_creds_dir())

        with open(self.get_config_path(), 'w') as f:
            template = Template(NSD_CONF_TEMPLATE)
            conf = template.render(
                creds_dir=settings.CREDS_DIR,
                hostname=self.hostname)
            f.write(conf)

    def get_zone_list(self):
        try:
            zs_out = subprocess.check_output(
                ["/usr/sbin/nsd-control",
                "-c", self.get_config_path(),
                "-s", self.hostname,
                "zonestatus"],
                stderr=subprocess.STDOUT,
            ).decode('utf-8')
        except subprocess.CalledProcessError:
            raise
        zones = ZONE_RE.findall(zs_out, re.MULTILINE)
        zone_data = {}
        zone_data['stats'] = {}
        zone_data['stats']['zone_stats'] = {}

        for zone in zones:
            zone_data['stats']['zone_stats'][zone] = {}
            zone_data['stats']['zone_stats'][zone]["no_view"] = {}
            zone_data['stats']['zone_stats'][zone]["no_view"]["serial"] =  "n/a"
        return zone_data
