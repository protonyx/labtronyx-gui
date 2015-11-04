import wx

from labtronyxgui.bases.view import ViewBase


class FrameViewBase(wx.Frame, ViewBase):
    def __init__(self, parent, controller, **kwargs):
        wx.Frame.__init__(self, parent=parent, **kwargs)
        ViewBase.__init__(self, controller)


class PanelViewBase(wx.Panel, ViewBase):
    def __init__(self, parent, controller, **kwargs):
        wx.Panel.__init__(self, parent=parent, **kwargs)
        ViewBase.__init__(self, controller)


class DialogViewBase(wx.Dialog, ViewBase):
    def __init__(self, parent, controller, **kwargs):
        wx.Dialog.__init__(self, parent=parent, **kwargs)
        ViewBase.__init__(self, controller)