"""
pyconfd example template plugin. This file is loaded by pyconfd. The get
function is called by pyconfd and returns the current dictionary of values to
populate the template with. If the values are different, the template generator
is executed and the target service reloads.

this goes here: /etc/pyconfd/conf.d/haproxy.py
"""
import subprocess
import shlex
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
    reload_cmd = "/usr/sbin/haproxy -f {{ dest }} -p /var/run/haproxy.pid -sf $(pidof haproxy)"
    reload_cmd = "supervisorctl restart haproxy"

    def get(self):
        """
        Get relevant variables from consul.

        :rtype: dict
        """
        session = consulate.Consulate()

        # track number of servers
        counter = 0

        # prepare data for jinja to consume for the jinja template
        data = {"servers": {}}

        # get a list of available servers in the cluster
        accessible_addresses = [srv["Addr"] for srv in session.agent.members()]

        # session.catalog.services() returns a list with a single dictionary
        services = session.catalog.services()

        # get all names of services provided by cluster
        service_keys = []
        if isinstance(services, list) and len(services) > 0 and isinstance(services[0], dict):
            service_keys = services[0].keys()
        elif isinstance(services, dict):
            service_keys = services.keys()

        for service in service_keys:
            data["servers"][service] = []

            # figure out servers with that service
            servers = session.catalog.service(service)

            for server in servers:
                ip_address = server["Address"]

                # only add server if it's in the current cluster
                if ip_address in accessible_addresses:
                    data["servers"][service].append((counter, ip_address))
                    counter += 1

        return data

    def reload_process(self):
        """
        Graceful reload if haproxy is already running.
        """
        try:
            output = subprocess.check_output(["pidof", "haproxy"])
            pids = output.strip()
        except Exception as exc:
            command = "/usr/sbin/haproxy -f {{ dest }} -p /var/run/haproxy.pid"
        else:
            command = "/usr/sbin/haproxy -f {{ dest }} -p /var/run/haproxy.pid -sf $(echo xyz)"
            command = command.replace("xyz", " ".join(pids))

        command = command.replace("{{ dest }}", self.dest)
        print "Running reload_cmd: {}".format(command)

        args = shlex.split(command)
        process = subprocess.Popen(args)
