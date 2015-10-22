
class BaseController(object):

    def __init__(self):
        self.views = []

    def registerView(self, view_obj):
        self.views.append(view_obj)

    def notifyViews(self, event, args):
        for v in self.views:
            try:
                v.handleEvent(event, args)

            except Exception as e:
                pass