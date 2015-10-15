__author__ = 'kkennedy'

import labtronyx

class LabManagerController(object):


    def __init__(self):
        self.model = labtronyx.LabManager()

    def add_host(self, hostname, port):
        self.model.addManager(hostname, port)

    def remove_host(self, hostname):
        self.model.removeManager(hostname)

    def list_hosts(self):
        self.model.getConnectedHosts()

    def list_resources(self):
        self.model.findResources()

    def get_resource(self, hostname, interface, resource_id, driver):
        pass