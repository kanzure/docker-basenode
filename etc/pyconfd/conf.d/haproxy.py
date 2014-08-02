"""
pyconfd example template plugin. This file is loaded by pyconfd. The get
function is called by pyconfd and returns the current dictionary of values to
populate the template with. If the values are different, the template generator
is executed and the target service reloads.

this goes here: /etc/pyconfd/conf.d/haproxy.py
"""

import pyconfd
import consulate

class HAProxyPlugin(pyconfd.Plugin):

    # config template is from /etc/pyconfd/templates/
    src = "haproxy.cfg.tmpl"

    # where to dump the generated config
    dest = "/etc/haproxy/haproxy.cfg"

    # check generated config file (not mandatory)
    check_cmd = "/usr/sbin/haproxy -c -q -f {{ dest }}"

    # Safely reload the process. Also, if you are using supervisord you can run
    # "supervisordctl reload haproxy", but it would drop active connections.
    reload_cmd = "/usr/sbin/haproxy -f {{ dest }} -p /var/run/haproxy.pid -sf $(</var/run/haproxy.pid)"

    def get(self):
        """
        Get relevant variables from consul.

        :rtype: dict
        """
        data = {"servers": {}}
        session = consulate.Consulate()
        services = session.catalog.services().keys()
        for service in services:
            data["servers"][service] = []
            servers = session.catalog.service(service)
            for server in servers:
                ip_address = server["Address"]
                data["servers"][service].append(ip_address)
        return data
