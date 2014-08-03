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

        # session.catalog.services() returns a list with a single dictionary
        services = session.catalog.services()

        service_keys = []
        if isinstance(services, list) and len(services) > 0 and isinstance(services[0], dict):
            service_keys = services[0].keys()
        elif isinstance(services, dict):
            service_keys = services.keys()

        for service in service_keys:
            data["servers"][service] = []
            servers = session.catalog.service(service)
            for server in servers:
                ip_address = server["Address"]
                data["servers"][service].append(ip_address)
        return data
