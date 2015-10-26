
class BaseController(object):

    def __init__(self):
        self._views = []

    def registerView(self, view_obj):
        self._views.append(view_obj)

    def unregisterView(self, view_obj):
        self._views.remove(view_obj)

    def notifyViews(self, event):
        for v in self._views:
            try:
                v.handleEvent(event)

            except Exception as e:
                pass

    def _handleEvent(self, event):
        pass