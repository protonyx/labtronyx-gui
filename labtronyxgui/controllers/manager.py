__author__ = 'kkennedy'

import labtronyx
from . import BaseController
from .resource import ResourceController


class ManagerController(BaseController):
    """
    Wraps RemoteManager
    """

    def __init__(self, ip_address, port=None):
        BaseController.__init__(self)

        self._resources = {}

        # Attempt to connect
        try:
            # Use a shorter timeout to keep the GUI responsive
            self._remoteManager = labtronyx.RemoteManager(host=ip_address, port=port, timeout=1.0)

            # Build cache of resources
            self._refresh()

        except labtronyx.RpcServerNotFound:
            self.status = "offline"

    def _handleEvent(self, event):
        pass

    def _refresh(self):
        self._remoteManager.refresh()
        res_list = self._remoteManager.findResources()

        # Refresh resources
        for res in res_list:
            if res.uuid not in self._resources:
                remote = ResourceController(self, res)
                self._resources[res.uuid] = remote

        # Refresh driver list
        self._driverInfo = self._remoteManager.getDriverInfo()

    def get_resource(self, res_uuid):
        return self._resources.get(res_uuid)

    @property
    def resources(self):
        return self._resources

    @property
    def drivers(self):
        return self._driverInfo

    def list_drivers(self):
        return self.drivers.keys()

    def list_driver_vendors(self):
        return list(set([v.get('deviceVendor', 'Unknown') for k,v in self.drivers.items()]))

    def list_drivers_from_vendor(self, vendor):
        return [k for k,v in self.drivers.items() if v.get('deviceVendor') == vendor]

    def list_driver_models_from_vendor(self, vendor):
        import itertools
        models = list([v.get('deviceModel') for k,v in self.drivers.items() if v.get('deviceVendor') == vendor])
        return list(set(itertools.chain(*models)))

    def list_drivers_vendor_model(self, vendor, model):
        return [k for k,v in self.drivers.items() if v.get('deviceVendor') == vendor and model in v.get('deviceModel')]

    def list_resources(self):
        return self._resources.keys()