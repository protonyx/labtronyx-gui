__author__ = 'kkennedy'

import labtronyx
from . import BaseController

class ResourceController(BaseController):
    """
    Wraps RemoteResource
    """

    def __init__(self, manager_controller, remote_resource):
        super(ResourceController, self).__init__()

        self._manager_controller = manager_controller
        self._model = remote_resource

    @property
    def model(self):
        return self._model

    @property
    def manager(self):
        return self._manager_controller

    @property
    def properties(self):
        return self._model.properties