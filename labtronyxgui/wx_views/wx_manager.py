import wx
from . import FrameViewBase, PanelViewBase, DialogViewBase

from labtronyx.common import events


class ScriptBrowserPanel(PanelViewBase):
    def __init__(self, parent, controller):
        super(ScriptBrowserPanel, self).__init__(parent, controller, id=wx.ID_ANY)

        self.tree = wx.TreeCtrl(self, -1, style=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT)
        self.pnode_root = self.tree.AddRoot("Scripts")  # Add hidden root item
        self.tree.SetPyData(self.pnode_root, None)

        self.panel_detail = wx.Panel(self)
        self.panel_detail.SetMinSize((250, -1))

        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.e_OnTreeSelect)

        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainSizer.Add(self.tree, 1, wx.EXPAND)
        self.mainSizer.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), 0, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.panel_detail, 0, wx.EXPAND)
        self.SetSizer(self.mainSizer)

        self.updateTree()

    def updateTree(self):
        self.tree.DeleteChildren(self.pnode_root)
        attributes = self.controller.get_script_attributes()

        categories = set([attr.get('category') for fqn, attr in attributes.items()])
        self.nodes_categories = {}

        for cat in categories:
            child = self.tree.AppendItem(self.pnode_root, cat)
            self.nodes_categories[cat] = child

        for fqn, attr in attributes.items():
            cat_node = self.nodes_categories.get(attr.get('category'))

            child = self.tree.AppendItem(cat_node, fqn)
            self.tree.SetPyData(child, fqn)

        #     subcategories = set([attr.get('subcategory') for fqn, attr in attributes.items()
        #                          if attr.get('category') == categories])

    def clearScriptSummary(self):
        self.panel_detail.DestroyChildren()

    def loadScriptSummary(self, fqn):
        self.panel_detail.Freeze()
        self.clearScriptSummary()

        new_panel = ScriptSummaryPanel(self.panel_detail, self.controller, fqn)

        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_sizer.Add(new_panel, 1, wx.EXPAND)
        self.panel_detail.SetSizer(panel_sizer)
        self.panel_detail.Layout()

        self.panel_detail.Thaw()

    def e_OnTreeSelect(self, event):
        item = event.GetItem()
        item_data = self.tree.GetPyData(item)

        if item_data is not None:
            self.loadScriptSummary(item_data)

        else:
            self.clearScriptSummary()


class ScriptSummaryPanel(PanelViewBase):
    def __init__(self, parent, controller, fqn):
        super(ScriptSummaryPanel, self).__init__(parent, controller, id=wx.ID_ANY)

        self.mainSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
        self.attributes = self.controller.attributes.get(fqn, {})

        # Controls
        self._createField("Script Name", "name")
        self._createField("Description", "description")
        self._createField("Category", "category")

        if self.attributes.get("subcategory") != '':
            self._createField("Subcategory", "subcategory")

        self.mainSizer.AddGrowableCol(1)

        self.SetSizer(self.mainSizer)
        self.SetAutoLayout(True)

    def _handleEvent(self, event):
        pass

    def _createField(self, label, prop_key):
        lblNew = wx.StaticText(self, -1, label + ":")
        txtNew = wx.StaticText(self, -1, self.attributes.get(prop_key))
        txtNew.Wrap(170)

        self.mainSizer.Add(lblNew, 0, wx.ALIGN_RIGHT | wx.RIGHT, 5)
        self.mainSizer.Add(txtNew, 1, wx.ALIGN_LEFT | wx.EXPAND)