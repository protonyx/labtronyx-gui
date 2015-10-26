__author__ = 'kkennedy'

import labtronyx
from . import BaseController

class ResourceController(BaseController):
    """
    Wraps RemoteResource
    """

    def __init__(self, remote_resource):
        BaseController.__init__(self)

        self._remote = remote_resource

    @property
    def properties(self):
        return self._remote.properties