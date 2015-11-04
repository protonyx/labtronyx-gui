__author__ = 'kkennedy'

import wx
import wx.lib.sized_controls
from . import FrameViewBase, PanelViewBase, DialogViewBase

from labtronyx.common import events

class ResourceControlView(FrameViewBase):
    def __init__(self, parent, controller):
        super(ResourceControlView, self).__init__(parent, controller, id=-1, style=wx.DEFAULT_FRAME_STYLE)

        # self.lbl_resource = wx.StaticText(self, -1, "Resource: %s" % self.controller.properties.get("resourceID"))

        self.pnl_driver = DriverSelectorPanel(self, controller)


class ResourcePropertiesView(FrameViewBase):
    def __init__(self, parent, controller):
        super(ResourcePropertiesView, self).__init__(parent, controller, id=-1, style=wx.DEFAULT_FRAME_STYLE)

        self.pnl_info = ResourceInfoPanel(self, controller)


class ResourceInfoPanel(PanelViewBase):
    def __init__(self, parent, controller):
        super(ResourceInfoPanel, self).__init__(parent, controller, id=wx.ID_ANY)

        self.mainSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
        self._fields = {}
        self.props = {}

        # Controls
        self._createField("Resource ID", "resourceID")
        self._createField("Resource Type", "resourceType")
        self._createField("Interface Name", "interface")
        self._createField("Driver", "driver")

        # self.pnl_driver = wx.Panel(self, -1)
        self.btn_driver = wx.Button(self, -1, "Driver")
        self.mainSizer.Add((10, 10))
        self.mainSizer.Add(self.btn_driver, 0, wx.ALIGN_LEFT)
        self.Bind(wx.EVT_BUTTON, self.e_DriverOnClick, self.btn_driver)

        self.SetSizer(self.mainSizer)
        self.mainSizer.Fit(self)

        self.updateFields()

    def handleEvent(self, event):
        if event.event in [events.EventCodes.resource.driver_loaded, events.EventCodes.resource.driver_unloaded,
                           events.EventCodes.resource.changed]:
            self.updateFields()

    def _createField(self, label, prop_key):
        lblNew = wx.StaticText(self, -1, label + ":")
        self._fields[prop_key] = wx.StaticText(self, -1, "")

        self.mainSizer.Add(lblNew, 0, wx.ALIGN_RIGHT)
        self.mainSizer.Add(self._fields[prop_key], 0, wx.EXPAND)

    def updateFields(self):
        self.props = self.controller.properties

        for prop_key, field in self._fields.items():
            field.SetLabelText(self.props.get(prop_key, ''))

        if self.props.get('driver', '') == '':
            self.btn_driver.SetLabelText("Load Driver")

        else:
            self.btn_driver.SetLabelText("Unload Driver")

    def e_DriverOnClick(self, event):
        if self.props.get('driver', '') == '':
            # Open load driver panel as a dialogue
            drv_dlg = DriverLoadDialog(self, self.controller)
            # drv_dlg.CenterOnScreen()

            val = drv_dlg.ShowModal()

            if val == wx.ID_OK:
                driver = drv_dlg.getSelectedDriver()

                if driver != '':
                    self.controller.load_driver(driver)

                else:
                    msg = wx.MessageDialog(self, 'No driver was selected', 'Load driver error', wx.OK|wx.ICON_ERROR)
                    msg.ShowModal()
                    msg.Destroy()

        else:
            self.controller.unload_driver()


class DriverLoadDialog(DialogViewBase):
    def __init__(self, parent, controller):
        super(DriverLoadDialog, self).__init__(parent, controller, id=wx.ID_ANY, title="Load Driver...")

        lbl = wx.StaticText(self, -1, "Select a driver to load")
        lbl.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.drv_select = DriverSelectorPanel(self, controller)
        btnOk = wx.Button(self, wx.ID_OK, "&Ok")
        btnOk.SetDefault()
        btnCancel = wx.Button(self, wx.ID_CANCEL, "&Cancel")

        btnSizer = wx.StdDialogButtonSizer()
        btnSizer.AddButton(btnOk)
        btnSizer.AddButton(btnCancel)
        btnSizer.Realize()

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(lbl,                 0, wx.ALL|wx.ALIGN_CENTER, border=5)
        mainSizer.Add(self.drv_select,     0, wx.EXPAND|wx.ALL, border=5)
        mainSizer.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, border=10)
        mainSizer.Add(btnSizer,            0, wx.ALL|wx.ALIGN_RIGHT, border=5)

        self.SetSizer(mainSizer)
        mainSizer.Fit(self)

    def getSelectedDriver(self):
        return self.drv_select.getSelectedDriver()

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
        vendors = ["Any"] + vendors

        self.panel_form = wx.lib.sized_controls.SizedPanel(self, -1)
        self.panel_form.SetSizerType("form")

        wx.StaticText(self.panel_form, -1, "Vendor")
        self.w_vendor = wx.Choice(self.panel_form, -1, size=(200, -1), choices=vendors)
        self.w_vendor.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.OnVendorChange, self.w_vendor)

        wx.StaticText(self.panel_form, -1, "Model")
        self.w_model = wx.Choice(self.panel_form, -1, size=(200, -1), choices=[])
        self.Bind(wx.EVT_CHOICE, self.OnModelChange, self.w_model)

        wx.StaticText(self.panel_form, -1, "Driver")
        self.w_driver = wx.Choice(self.panel_form, -1, size=(200, -1), choices=[])

        self.updateModels()
        self.updateDrivers()

        self.panel_form.Fit()
        self.SetSize(self.panel_form.GetSize())

    def getSelectedDriver(self):
        return self.w_driver.GetStringSelection()

    def OnVendorChange(self, event):
        self.updateModels()
        self.updateDrivers()

    def OnModelChange(self, event):
        self.updateDrivers()

    def updateModels(self):
        if self.w_vendor.GetSelection() == 0:
            models = ["Any"]

        else:
            vendor = self.w_vendor.GetStringSelection()

            models = self.controller.manager.list_driver_models_from_vendor(vendor)
            models.sort()

            models = ["Any"] + models

        self.w_model.Clear()
        self.w_model.AppendItems(models)
        self.w_model.SetSelection(0)

    def updateDrivers(self):
        vend_sel = self.w_vendor.GetSelection()
        vendor = self.w_vendor.GetStringSelection()
        mod_sel = self.w_model.GetSelection()
        model = self.w_model.GetStringSelection()

        if vend_sel == 0 and mod_sel == 0:
            drivers = self.controller.manager.get_drivers()

        elif mod_sel == 0:
            drivers = self.controller.manager.get_drivers_from_vendor(vendor)

        else:
            drivers = self.controller.manager.get_drivers_from_vendor_model(vendor, model)

        driver_list = sorted(drivers.keys())

        self.w_driver.Clear()
        self.w_driver.AppendItems(driver_list)