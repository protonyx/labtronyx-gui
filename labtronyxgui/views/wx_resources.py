__author__ = 'kkennedy'

import wx
from labtronyxgui.bases.wx_view import ViewBase

class ResourceControlView(ViewBase):
    def __init__(self):
        ViewBase.__init__(self)

        self.pnl_driver = DriverPanel(parent=self, id=wx.ID_ANY, style=wx.WANTS_CHARS)

class DriverPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

class ResourcePropertiesView(ViewBase):
    pass


