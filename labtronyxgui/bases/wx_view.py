__author__ = 'kkennedy'

import wx

class ViewBase(object):

    def __init__(self, controller):
        self._controller = controller
        self._controller.registerView(self)

    @property
    def controller(self):
        return self._controller


class FrameViewBase(wx.Frame, ViewBase):
    def __init__(self, parent, controller, **kwargs):
        wx.Frame.__init__(self, parent=parent, **kwargs)
        ViewBase.__init__(self, controller)


class PanelViewBase(wx.Panel, ViewBase):
    def __init__(self, parent, controller, **kwargs):
        wx.Panel.__init__(self, parent=parent, **kwargs)
        ViewBase.__init__(self, controller)