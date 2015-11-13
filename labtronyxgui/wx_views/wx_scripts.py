import wx

import labtronyx

from ..controllers import ScriptController
from . import FrameViewBase, PanelViewBase, DialogViewBase


class ScriptInfoPanel(PanelViewBase):
    def __init__(self, parent, controller):
        assert(isinstance(controller, ScriptController))
        super(ScriptInfoPanel, self).__init__(parent, controller, id=wx.ID_ANY)

        self.props = self.controller.properties
        self.param_info = self.controller.parameters

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.topSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.midSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.attr_sizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
        self.param_sizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)

        # Top section
        self._fieldAttributes("Script UUID", "uuid")
        self._fieldAttributes("Script Name", "name")
        self._fieldAttributes("Description", "description")
        self._fieldAttributes("Category", "category")

        for param, param_details in self.param_info.items():
            self._fieldParameters(param, param)

        self.attr_sizer.AddGrowableCol(1)
        self.param_sizer.AddGrowableCol(1)

        self.topSizer.Add(self.attr_sizer, 1, wx.EXPAND)
        self.topSizer.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), 0, wx.EXPAND | wx.ALL, 5)
        self.topSizer.Add(self.param_sizer, 1, wx.EXPAND)

        # Middle section
        # start/stop, status, progress?
        self.btn_do = wx.Button(self, -1, "Do")
        self.txt_state = wx.StaticText(self, -1, "")
        self.Bind(wx.EVT_BUTTON, self.e_OnButton, self.btn_do)

        self.midSizer.Add(self.btn_do, 0, wx.ALIGN_LEFT)
        self.midSizer.Add(self.txt_state, 1, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT, 10)

        # Lower section
        # notebook: resources, log, results

        self.mainSizer.Add(self.topSizer, 1)
        self.mainSizer.Add(self.midSizer, 0)

        self.SetSizer(self.mainSizer)
        self.SetAutoLayout(True)
        self.mainSizer.Fit(self)
        self.Fit()

    def _handleEvent(self, event):
        if event.event in [labtronyx.EventCodes.script.changed]:
            self.update()

    def update(self):
        self.txt_state.SetLabelText(self.controller.properties.get('status'))

    def _fieldAttributes(self, label, attr_key):
        lblNew = wx.StaticText(self, -1, label + ":")
        value = self.props.get(attr_key) or ''
        txtNew = wx.StaticText(self, -1, value)

        self.attr_sizer.Add(lblNew, 0, wx.ALIGN_RIGHT | wx.RIGHT, 5)
        self.attr_sizer.Add(txtNew, 1, wx.ALIGN_LEFT | wx.EXPAND)

    def _fieldParameters(self, label, prop_key):
        lblNew = wx.StaticText(self, -1, label + ":")
        value = self.props.get(prop_key) or ''
        txtNew = wx.StaticText(self, -1, value)

        self.param_sizer.Add(lblNew, 0, wx.ALIGN_RIGHT | wx.RIGHT, 5)
        self.param_sizer.Add(txtNew, 1, wx.ALIGN_LEFT | wx.EXPAND)

    def e_OnButton(self, event):
        self.controller.start()


class ScriptParametersDialog(DialogViewBase):
    def __init__(self, parent, controller=None):
        assert (isinstance(controller, ScriptController))
        super(ScriptParametersDialog, self).__init__(parent, controller, id=wx.ID_ANY, title="Script Parameters")

        if self.controller is None:
            lbl = wx.StaticText(self, -1, "Open Script")
        else:
            lbl = wx.StaticText(self, -1, "Script")
        lbl.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.pnl_main = ScriptParametersPanel(self, self.controller)

        btnOk = wx.Button(self, wx.ID_OK, "&Ok")
        btnOk.SetDefault()
        btnCancel = wx.Button(self, wx.ID_CANCEL, "&Cancel")

        btnSizer = wx.StdDialogButtonSizer()
        btnSizer.AddButton(btnOk)
        btnSizer.AddButton(btnCancel)
        btnSizer.Realize()

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(lbl, 0, wx.EXPAND | wx.ALL, border=5)
        mainSizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, border=5)
        mainSizer.Add(self.pnl_main, 0, wx.EXPAND | wx.ALL, border=5)
        mainSizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, border=5)
        mainSizer.Add(btnSizer, 0, wx.ALL | wx.ALIGN_RIGHT, border=5)

        self.SetSizer(mainSizer)
        mainSizer.Fit(self)


class ScriptParametersPanel(PanelViewBase):
    pass