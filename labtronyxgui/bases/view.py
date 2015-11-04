
class ViewBase(object):

    def __init__(self, controller):
        self._controller = controller
        self._controller.registerView(self)

    def __del__(self):
        self._controller.unregisterView(self)

    @property
    def controller(self):
        return self._controller

    def handleEvent(self, event):
        pass