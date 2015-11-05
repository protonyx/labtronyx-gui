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

        self._uuid = self._model.uuid
        self._resID = self._model.resID

    def _handleEvent(self, event):
        resource_events = labtronyx.common.events.EventCodes.resource

        # Check that the event was for us
        if len(event.args) > 0 and event.args[0] == self._uuid:
            if event.event in [resource_events.driver_loaded, resource_events.driver_unloaded, resource_events.changed]:
                self.notifyViews(event)

    @property
    def model(self):
        return self._model

    @property
    def resID(self):
        return self._resID

    @property
    def manager(self):
        return self._manager_controller

    @property
    def properties(self):
        return self._model.getProperties()

    def load_driver(self, new_driver):
        return self._model.loadDriver(new_driver)

    def unload_driver(self):
        return self._model.unloadDriver()