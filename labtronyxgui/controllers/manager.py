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
            self._remoteManager = labtronyx.RemoteManager(host=ip_address, port=port)

            # Build cache of resources
            self._refresh()

        except labtronyx.RpcServerNotFound:
            self.status = "offline"

    def _handleEvent(self, event):
        pass

    def _refresh(self):
        self._remoteManager.refresh()
        res_list = self._remoteManager.findResources()

        for res in res_list:
            if res.uuid not in self._resources:
                remote = ResourceController(res)
                self._resources[res.uuid] = remote

    def get_resource(self, res_uuid):
        return self._resources.get(res_uuid)

    @property
    def resources(self):
        return self._resources

    def list_resources(self):
        return self._resources.keys()