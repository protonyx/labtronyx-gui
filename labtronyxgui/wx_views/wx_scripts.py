import wx
from . import FrameViewBase, PanelViewBase, DialogViewBase

from labtronyx.common import events


class ScriptInfoPanel(PanelViewBase):
    def __init__(self, parent, controller):
        super(ScriptInfoPanel, self).__init__(parent, controller, id=wx.ID_ANY)

        self.mainSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
        self._fields = {}
        self.props = {}

        # Controls
        self._createField("Script Name", "name")
        self._createField("Description", "description")
        self._createField("Category", "category")

        self.mainSizer.AddGrowableCol(1)

        self.SetSizer(self.mainSizer)
        self.SetAutoLayout(True)

        self.updateFields()

    def _handleEvent(self, event):
        if event.event in [events.EventCodes.resource.driver_loaded, events.EventCodes.resource.driver_unloaded,
                           events.EventCodes.resource.changed]:
            self.updateFields()

    def _createField(self, label, prop_key):
        lblNew = wx.StaticText(self, -1, label + ":")
        self._fields[prop_key] = wx.StaticText(self, -1, "")

        self.mainSizer.Add(lblNew, 0, wx.ALIGN_RIGHT | wx.RIGHT, 5)
        self.mainSizer.Add(self._fields[prop_key], 1, wx.ALIGN_LEFT | wx.EXPAND)

    def updateFields(self):
        self.props = self.controller.properties

        for prop_key, field in self._fields.items():
            field.SetLabelText(self.props.get(prop_key, ''))

        # Refresh panel since item lengths may have changed
        self.mainSizer.Fit(self)
        self.Fit()