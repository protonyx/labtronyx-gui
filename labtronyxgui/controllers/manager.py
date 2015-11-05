__author__ = 'kkennedy'

import labtronyx
from . import BaseController
from .resource import ResourceController


class ManagerController(BaseController):
    """
    Wraps RemoteManager
    """

    def __init__(self, model):
        BaseController.__init__(self)

        self._model = model

        self._hostname = self._model.getHostname()

        # Update Resources
        self._resources = {}
        self._refresh()

        # Get driver list
        self._driverInfo = self._model.getDriverInfo()

    @property
    def model(self):
        return self._model

    def _handleEvent(self, event):
        # Check if this event is for us
        if event.hostname == self._hostname:
            for res_uuid, res_con in self._resources.items():
                try:
                    res_con._handleEvent(event)
                except Exception:
                    pass

            self.notifyViews(event)

    def _refresh(self):
        self.model.refresh()

        # Create controllers for each of the model resources
        for res_uuid, resObj in self.model.resources.items():
            if res_uuid not in self._resources:
                remote = ResourceController(self, resObj)
                self._resources[res_uuid] = remote

    def get_resource(self, res_uuid):
        return self._resources.get(res_uuid)

    @property
    def hostname(self):
        return self._hostname

    @property
    def resources(self):
        return self._resources

    @property
    def drivers(self):
        return self._driverInfo

    def list_drivers(self):
        return self.drivers.keys()

    def list_driver_vendors(self):
        vendors = set()

        for driver_name, driver_info in self.drivers.items():
            for comp_vendor, comp_models in driver_info.get('compatibleInstruments', {}).items():
                vendors.add(comp_vendor)

        return list(vendors)

    def list_driver_models_from_vendor(self, vendor):
        models = set()

        for driver_name, driver_info in self.drivers.items():
            for comp_vendor, comp_models in driver_info.get('compatibleInstruments', {}).items():
                if vendor == comp_vendor:
                    models.update(comp_models)

        return list(models)

    def get_drivers(self):
        return self.drivers

    def get_drivers_from_vendor(self, vendor):
        drivers = {}

        for driver_name, driver_info in self.drivers.items():
            for comp_vendor, comp_models in driver_info.get('compatibleInstruments', {}).items():
                if vendor == comp_vendor:
                    drivers[driver_name] = driver_info

        return drivers

    def get_drivers_from_vendor_model(self, vendor, model):
        drivers = {}

        for driver_name, driver_info in self.drivers.items():
            for comp_vendor, comp_models in driver_info.get('compatibleInstruments', {}).items():
                if vendor == comp_vendor and model in comp_models:
                    drivers[driver_name] = driver_info

        return drivers

    def filter_compatible_drivers(self, drivers, interfaceName):
        return {k:v for k,v in drivers.items() if interfaceName in v.get('compatibleInterfaces', [])}

    def list_resources(self):
        return self._resources.keys()