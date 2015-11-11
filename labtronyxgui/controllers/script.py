__author__ = 'kkennedy'

import labtronyx
from . import BaseController


class ScriptController(BaseController):
    def __init__(self, manager_controller, model):
        super(ScriptController, self).__init__()

        self._manager_controller = manager_controller
        self._model = model

        # Cache properties
        self._properties = {}
        self.update_properties()

        self._uuid = self._properties.get('uuid')

    def update_properties(self):
        self._properties = self._model.getProperties()

    @property
    def manager(self):
        return self._manager

    @property
    def uuid(self):
        return self._uuid

    @property
    def properties(self):
        return self._properties