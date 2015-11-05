__author__ = 'kkennedy'

import labtronyx
from . import BaseController

class ResourceController(BaseController):
    """
    Wraps RemoteResource
    """

    def __init__(self, manager_controller, model):
        super(ResourceController, self).__init__()

        self._manager_controller = manager_controller
        self._model = model

        # Cache properties
        self._properties = {}
        self.update_properties()

        self._uuid = self._properties.get('uuid')
        self._resID = self._properties.get('resourceID')

    def _handleEvent(self, event):
        resource_events = labtronyx.common.events.EventCodes.resource

        # Check that the event was for us
        if len(event.args) > 0 and event.args[0] == self._uuid:
            if event.event in [resource_events.driver_loaded, resource_events.driver_unloaded, resource_events.changed]:
                self.update_properties()
                self.notifyViews(event)

    def update_properties(self):
        self._properties = self._model.getProperties()

    @property
    def manager(self):
        return self._manager_controller

    @property
    def model(self):
        return self._model

    @property
    def properties(self):
        return self._properties

    @property
    def uuid(self):
        return self._uuid

    @property
    def resID(self):
        return self._resID

    def load_driver(self, new_driver):
        return self._model.loadDriver(new_driver)

    def unload_driver(self):
        return self._model.unloadDriver()