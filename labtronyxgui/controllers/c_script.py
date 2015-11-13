__author__ = 'kkennedy'

import labtronyx
from . import PluginController


class ScriptController(PluginController):
    def __init__(self, c_manager, model):
        super(ScriptController, self).__init__(c_manager, model)

        self._attributes = self.model.getAttributes()  # values
        self._parameters = self.model.getParameterInfo()  # class data

    def _handleEvent(self, event):
        # Check that the event was for us
        if len(event.args) > 0 and event.args[0] == self._uuid:
            if event.event in [labtronyx.EventCodes.script.changed]:
                self.update_properties()

            self.notifyViews(event)

    @property
    def attributes(self):
        return self._attributes

    @property
    def parameters(self):
        return self._parameters

    def start(self):
        self.model.start()