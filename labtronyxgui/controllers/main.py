__author__ = 'kkennedy'

import socket

import labtronyx

class MainApplicationController(object):

    def __init__(self):
        self.model = labtronyx.LabManager()

        self.event_sub = labtronyx.EventSubscriber()

        self.hosts = {}

        # Try to connect to a local instance first
        self.add_host('localhost')

    def resolveHost(self, host):
        """
        Resolve a host to an IPv4 address. If the host is already an IP address, it will be returned without modification

        :param host:    hostname or IP address
        :return:        IP address
        """
        try:
            socket.inet_aton(host)
            return host

        except socket.error:
            # Invalid address
            return socket.gethostbyname(host)

    def networkHostname(self, ip_address):
        return socket.gethostbyaddr(ip_address)[0]

    def add_host(self, hostname, port=None):
        ip_address = self.resolveHost(hostname)

        if ip_address not in self.hosts:
            try:
                remote = labtronyx.RemoteManager(host=ip_address, port=port)
                self.event_sub.connect(ip_address)

                # Force an RPC request
                remote.getVersion()

                self.hosts[ip_address] = remote

                return True

            except labtronyx.RpcServerNotFound:
                return False

        return False

    def remove_host(self, hostname):
        ip_address = self.resolveHost(hostname)

        if ip_address in self.hosts:
            host = self.hosts.pop(ip_address)
            del host

            self.event_sub.disconnect(ip_address)

    def list_hosts(self):
        return self.hosts.keys()

    def list_resources(self, host):
        """
        Get a list of Resource UUIDs for a given host

        :param host:
        :return:
        """
        ip_address = self.resolveHost(host)
        host = self.hosts.get(ip_address)

        if host is not None:
            all_props = host.getProperties()

            return all_props.keys()

    def get_resource_properties(self, res_uuid):
        for ip_address, remote_man in self.hosts.items():
            res = remote_man._getResource(res_uuid)

            if res is not None:
                return res.getProperties()

        return {}