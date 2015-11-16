import sys
import wx

import labtronyx

from ..controllers import ScriptController
from . import FrameViewBase, PanelViewBase, DialogViewBase


class ScriptInfoPanel(PanelViewBase):
    def __init__(self, parent, controller):
        assert(isinstance(controller, ScriptController))
        super(ScriptInfoPanel, self).__init__(parent, controller, id=wx.ID_ANY)

        self.props = self.controller.properties

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.attr_sizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)

        # Top section
        # self._fieldAttributes("Script UUID", "uuid")
        self._fieldAttributes("Script Name", "name")
        self._fieldAttributes("Description", "description")
        self._fieldAttributes("Category", "category")

        self.attr_sizer.Add(wx.StaticText(self, -1, "State:"), 0, wx.ALIGN_RIGHT | wx.RIGHT, 5)
        self.txt_state = wx.StaticText(self, -1, "")
        self.attr_sizer.Add(self.txt_state, 0, wx.ALIGN_LEFT)
        self.attr_sizer.Add((10, 10))
        self.btn_do = wx.Button(self, -1, "")
        self.attr_sizer.Add(self.btn_do, 0, wx.ALIGN_LEFT)
        self.Bind(wx.EVT_BUTTON, self.e_OnButton, self.btn_do)

        self.attr_sizer.AddGrowableCol(1)

        # Lower section
        self.notebook = wx.Notebook(self, -1, style=wx.BK_DEFAULT)
        # Parameters
        self.nb_parameters = ScriptParametersPanel(self.notebook, self.controller)
        self.notebook.AddPage(self.nb_parameters, "Parameters")
        # Resources
        self.nb_resources = ScriptResourcesPanel(self.notebook, self.controller)
        self.notebook.AddPage(self.nb_resources, "Resources")
        # Status/Log
        self.nb_status = ScriptStatusPanel(self.notebook, self.controller)
        self.notebook.AddPage(self.nb_status, "Status")
        # Results
        self.nb_results = ScriptResultsPanel(self.notebook, self.controller)
        self.notebook.AddPage(self.nb_results, "Results")

        self.mainSizer.Add(self.attr_sizer, 0, wx.EXPAND)
        self.mainSizer.Add(self.notebook, 1, wx.EXPAND | wx.TOP, 10)

        self.SetSizer(self.mainSizer)
        self.SetAutoLayout(True)
        self.mainSizer.Fit(self)
        self.Fit()

        self.update()

    def _handleEvent(self, event):
        if event.event in [labtronyx.EventCodes.script.changed]:
            self.update()

    def update(self):
        properties = self.controller.properties
        results = properties.get('results', [])

        if properties.get('running', False):
            self.btn_do.SetLabelText('Stop')
        else:
            self.btn_do.SetLabelText('Start')

        if properties.get('running', False):
            self.txt_state.SetLabelText('Running')
            self.txt_state.SetForegroundColour(wx.YELLOW)

        elif len(results) > 0:
            last_result = results[-1].get('result', '')
            if last_result == labtronyx.ScriptResult.PASS:
                self.txt_state.SetLabelText('PASS')
                self.txt_state.SetForegroundColour(wx.GREEN)

            elif last_result == labtronyx.ScriptResult.FAIL:
                self.txt_state.SetLabelText('FAIL')
                self.txt_state.SetForegroundColour(wx.RED)

            elif last_result == labtronyx.ScriptResult.STOPPED:
                self.txt_state.SetLabelText('STOPPED')
                self.txt_state.SetForegroundColour(wx.RED)

        elif properties.get('ready', False):
            self.txt_state.SetLabelText('Ready')
            self.txt_state.SetForegroundColour(wx.BLACK)

    def _fieldAttributes(self, label, attr_key):
        lblNew = wx.StaticText(self, -1, label + ":")
        value = self.props.get(attr_key) or ''
        txtNew = wx.StaticText(self, -1, value)

        self.attr_sizer.Add(lblNew, 0, wx.ALIGN_RIGHT | wx.RIGHT, 5)
        self.attr_sizer.Add(txtNew, 1, wx.ALIGN_LEFT | wx.EXPAND)

    def e_OnButton(self, event):
        properties = self.controller.properties
        if properties.get('running', False):
            self.controller.stop()
        else:
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
    def __init__(self, parent, controller):
        assert(isinstance(controller, ScriptController))
        super(ScriptParametersPanel, self).__init__(parent, controller, id=wx.ID_ANY)

        self.param_info = self.controller.parameters
        self.param_sizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)

        for param, param_details in self.param_info.items():
            self._fieldParameters(param, param)

        self.param_sizer.AddGrowableCol(1)
        self.SetSizer(self.param_sizer)

    def _fieldParameters(self, label, prop_key):
        lblNew = wx.StaticText(self, -1, label + ":")
        value = self.props.get(prop_key) or ''
        txtNew = wx.StaticText(self, -1, value)

        self.param_sizer.Add(lblNew, 0, wx.ALIGN_RIGHT | wx.RIGHT, 5)
        self.param_sizer.Add(txtNew, 1, wx.ALIGN_LEFT | wx.EXPAND)


class ScriptResourcesPanel(PanelViewBase):
    def __init__(self, parent, controller):
        assert(isinstance(controller, ScriptController))
        super(ScriptResourcesPanel, self).__init__(parent, controller, id=wx.ID_ANY)


class ScriptStatusPanel(PanelViewBase):
    def __init__(self, parent, controller):
        assert(isinstance(controller, ScriptController))
        super(ScriptStatusPanel, self).__init__(parent, controller, id=wx.ID_ANY)

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.topSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.status = wx.StaticText(self, -1)
        self.progress = wx.Gauge(self, -1, size=(-1, 25))
        self.log = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)

        self.topSizer.Add(self.status, 2, wx.RIGHT, 10)
        self.topSizer.Add(self.progress, 1)

        self.mainSizer.Add(self.topSizer, 0, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.log, 1, wx.EXPAND)

        self.SetSizer(self.mainSizer)
        self.refreshLog()

    def _handleEvent(self, event):
        if event.event in [labtronyx.EventCodes.script.changed]:
            self.update()

        elif event.event in [labtronyx.EventCodes.script.log]:
            if event.args[0] == self.controller.uuid:
                self.log.AppendText('\n' + event.args[1])

    def update(self):
        properties = self.controller.properties
        self.progress.SetValue(properties.get('progress'))

        self.status.SetLabelText(properties.get('status'))

    def refreshLog(self):
        log = self.controller.log
        log_txt = '\r\n'.join(log)
        self.log.SetEditable(True)
        self.log.SetLabelText(log_txt)
        self.log.SetEditable(False)

class ScriptResultsPanel(PanelViewBase):
    def __init__(self, parent, controller):
        assert(isinstance(controller, ScriptController))
        super(ScriptResultsPanel, self).__init__(parent, controller, id=wx.ID_ANY)

        self.list = ResultListCtrl(self, -1, style=wx.LC_REPORT)

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.list, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(self.mainSizer)

        self.update()

    def _handleEvent(self, event):
        if event.event in [labtronyx.EventCodes.script.changed]:
            results_displayed = self.list.GetItemCount()
            if len(self.controller.results) > results_displayed:
                self.update()

    def update(self):
        self.list.Freeze()

        self.list.ClearAll()
        self.list.InsertColumn(0, "Time")
        self.list.InsertColumn(1, "Result")
        self.list.InsertColumn(2, "Reason")
        self.list.InsertColumn(3, "Execution Time")

        properties = self.controller.properties
        results = reversed(self.controller.results)

        for res in results:
            res_time = self.controller.human_time(res.get('time', 0))
            idx = self.list.InsertStringItem(sys.maxint, res_time)
            self.list.SetStringItem(idx, 1, res.get('result', ''))
            self.list.SetStringItem(idx, 2, res.get('reason', ''))
            execTime = self.controller.human_time_delta(res.get('executionTime', 0))
            self.list.SetStringItem(idx, 3, execTime)

        self.list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.list.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
        self.list.SetColumnWidth(2, 225)
        self.list.SetColumnWidth(3, 135)

        self.list.Thaw()

class ResultListCtrl(wx.ListCtrl):
    pass