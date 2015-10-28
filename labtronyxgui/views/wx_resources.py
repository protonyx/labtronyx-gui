__author__ = 'kkennedy'

import wx
import wx.lib.sized_controls
from labtronyxgui.bases.wx_view import FrameViewBase, PanelViewBase

class ResourceControlView(FrameViewBase):
    def __init__(self, parent, controller):
        super(ResourceControlView, self).__init__(parent, controller, id=-1, style=wx.DEFAULT_FRAME_STYLE)

        # self.lbl_resource = wx.StaticText(self, -1, "Resource: %s" % self.controller.properties.get("resourceID"))

        self.pnl_driver = DriverSelectorPanel(self, controller)

class DriverSelectorPanel(PanelViewBase):
    """
    Driver Selection Widget

    :param controller:  Resource controller
    :type controller:   controllers.resource.ResourceController
    """
    def __init__(self, parent, controller):
        super(DriverSelectorPanel, self).__init__(parent, controller, id=wx.ID_ANY, style=wx.WANTS_CHARS)

        vendors = self.controller.manager.list_driver_vendors()
        vendors.sort()

        self.panel_form = wx.lib.sized_controls.SizedPanel(self, -1)
        self.panel_form.SetSizerType("form")

        wx.StaticText(self.panel_form, -1, "Vendor")
        self.w_vendor = wx.Choice(self.panel_form, -1, choices=vendors)
        self.Bind(wx.EVT_CHOICE, self.OnVendorChange, self.w_vendor)

        wx.StaticText(self.panel_form, -1, "Model")
        self.w_model = wx.Choice(self.panel_form, -1, choices=[])
        self.Bind(wx.EVT_CHOICE, self.OnModelChange, self.w_model)

        wx.StaticText(self.panel_form, -1, "Driver")
        self.w_driver = wx.Choice(self.panel_form, -1, choices=[])

        self.panel_form.Fit()

    def OnVendorChange(self, event):
        vendor = event.GetString()

        models = self.controller.manager.list_driver_models_from_vendor(vendor)
        models.sort()

        self.w_model.Clear()
        self.w_model.AppendItems(models)
        self.w_model.SetSelection(0)

    def OnModelChange(self, event):
        vendor = self.w_vendor.GetStringSelection()
        model = event.GetString()

        drivers = self.controller.manager.list_drivers_vendor_model(vendor, model)
        drivers.sort()

        self.w_driver.Clear()
        self.w_driver.AppendItems(drivers)
        self.w_driver.SetSelection(0)

class ResourcePropertiesView(FrameViewBase):
    pass


