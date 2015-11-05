import wx
import wx.aui
import wx.lib

from labtronyx.common import events
from . import FrameViewBase, PanelViewBase
from .wx_resources import ResourceInfoPanel

def main(controller):
    app = LabtronyxApp(controller)
    app.MainLoop()

class LabtronyxApp(wx.App):
    def __init__(self, controller):
        self._controller = controller
        wx.App.__init__(self)

    def OnInit(self):
        self.SetAppName("Labtronyx")

        main_view = MainView(self._controller)

        self.SetTopWindow(main_view)
        main_view.Show()

        return True


class MainView(FrameViewBase):
    """
    Labtronyx Top-Level Window
    """

    def __init__(self, controller):
        super(MainView, self).__init__(None, controller,
            id=-1, title="Labtronyx", size=(640, 480), style=wx.DEFAULT_FRAME_STYLE)

        self.mainPanel = wx.Panel(self)
        self.aui_mgr = wx.aui.AuiManager()
        self.aui_mgr.SetManagedWindow(self.mainPanel)

        # Build Menu
        self.buildMenubar()

        # Build Left Panel
        self.pnl_left = wx.Panel(self.mainPanel, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)
        # Resource Tree
        self.tree = wx.TreeCtrl(self.pnl_left, -1, style=wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT)
        self.host = wx.Choice(self.pnl_left, -1, style=wx.CB_SORT)
        self.updateHostSelector()
        self.host.SetSelection(0)
        host_select_sizer = wx.BoxSizer(wx.HORIZONTAL)
        host_select_sizer.Add(self.host, 1, wx.EXPAND)

        leftPanelSizer = wx.BoxSizer(wx.VERTICAL)
        leftPanelSizer.Add(wx.StaticText(self.pnl_left, -1, "Select Host"), 0, wx.ALL, 5)
        leftPanelSizer.Add(host_select_sizer, 0, wx.EXPAND|wx.BOTTOM, 5)
        leftPanelSizer.Add(self.tree, 1, wx.EXPAND)
        self.pnl_left.SetSizer(leftPanelSizer)
        # self.pnl_left.Fit()
        self.buildTree()

        # Build Main Panel
        self.pnl_content = wx.Panel(self.mainPanel, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN|wx.FULL_REPAINT_ON_RESIZE)

        # Build Log
        self.log = wx.TextCtrl(self.mainPanel, -1, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)

        # Event bindings
        self.Bind(wx.EVT_CHOICE, self.e_OnHostSelect, self.host)
        self.Bind(wx.EVT_CLOSE, self.e_OnWindowClose)

        self.SetBackgroundColour(wx.NullColour)
        self.SetSize((640, 480))
        # self.Fit()

        self.aui_mgr.AddPane(self.pnl_content, wx.aui.AuiPaneInfo().CenterPane().Name("Content"))
        self.aui_mgr.AddPane(self.log, wx.aui.AuiPaneInfo().Bottom().BestSize((-1, 200)).Caption("Log Messages").
                             Floatable(False).CloseButton(False).Name("LogPanel"))
        self.aui_mgr.AddPane(self.pnl_left, wx.aui.AuiPaneInfo().Left().BestSize((300, -1)).
                             Floatable(False).CloseButton(False).MinSize((240, -1)).Resizable(True).Caption("Resources").
                             Name("ResourceTree"))
        self.aui_mgr.Update()

    def buildMenubar(self):
        self.menubar = wx.MenuBar()

        # File
        self.menu_file = wx.Menu()
        item = self.menu_file.Append(-1, "E&xit\tCtrl-Q", "Exit")
        self.Bind(wx.EVT_MENU, self.e_MenuExit, item)

        self.menubar.Append(self.menu_file, "&File")

        # Set frame menubar
        self.SetMenuBar(self.menubar)

    def buildTree(self):
        # Build image list
        isz = (16, 16)
        self.il = wx.ImageList(*isz)
        self.art_host = self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_REMOVABLE, wx.ART_OTHER, isz))
        self.art_resource = self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))

        self.tree.SetImageList(self.il)

        self.pnode_root = self.tree.AddRoot("Labtronyx") # Add hidden root item
        self.tree.SetPyData(self.pnode_root, None)

        self.updateTree()
        # self.tree.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.e_OnRightClick)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.e_OnTreeSelect)

    def updateHostSelector(self):
        selected = self.host.GetStringSelection()

        choices = [hcon.hostname for hcon in self.controller.hosts.values()]

        self.host.Clear()
        self.host.AppendItems(choices)

        if selected in choices:
            self.host.SetStringSelection(selected)

    def get_selected_host_controller(self):
        hostname = self.host.GetStringSelection()
        return self.controller.get_host(hostname)

    def updateTree(self):
        host_controller = self.get_selected_host_controller()

        if host_controller is None:
            return

        self.tree.DeleteChildren(self.pnode_root)
        self.pnode_resources = self.tree.AppendItem(self.pnode_root, 'Resources')
        self.tree.SetItemImage(self.pnode_resources, self.art_resource)

        self.nodes_resources = {}

        for res_uuid, res_controller in host_controller.resources.items():
            # Add new resources
            res_prop = res_controller.properties

            # Resource Name
            node_name = res_prop.get('resourceID')

            child = self.tree.AppendItem(self.pnode_resources, node_name)
            self.tree.SetPyData(child, res_uuid)
            self.tree.SetItemImage(child, self.art_resource)
            self.nodes_resources[res_uuid] = child

        self.tree.SortChildren(self.pnode_resources)
        self.tree.Expand(self.pnode_resources)

    def e_MenuExit(self, event):
        self.Close(True)

    def e_OnWindowClose(self, event):
        self.Destroy()

    def e_OnTreeSelect(self, event):
        item = event.GetItem()
        item_data = self.tree.GetPyData(item)

        host_controller = self.get_selected_host_controller()

        if host_controller is not None:
            if item_data in host_controller.resources:
                # Resource
                self.loadResourcePanel(item_data)

    def e_OnHostSelect(self, event):
        self.updateTree()

    def loadResourcePanel(self, res_uuid):
        self.pnl_content.Freeze()

        host_controller = self.get_selected_host_controller()
        res_controller = host_controller.get_resource(res_uuid)

        # Build panel
        self.pnl_content.DestroyChildren()
        # self.pnl_content.ClearBackground()
        res_panel = ResourceInfoPanel(self.pnl_content, res_controller)
        # res_panel.SetBackgroundColour(wx.BLUE)

        lbl = wx.StaticText(self.pnl_content, -1, "Resource Details")
        lbl.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))

        panelSizer = wx.BoxSizer(wx.VERTICAL)
        panelSizer.Add(lbl,                             0, wx.EXPAND|wx.ALL, 5)
        panelSizer.Add(wx.StaticLine(self.pnl_content), 0, wx.EXPAND|wx.ALL, 5)
        panelSizer.Add(res_panel,                       1, wx.EXPAND|wx.ALL, 5)
        self.pnl_content.SetSizerAndFit(panelSizer)
        self.pnl_content.Layout()
        self.pnl_content.Refresh()



        self.pnl_content.Thaw()

    def _handleEvent(self, event):
        if event.event == events.EventCodes.manager.heartbeat:
            self.handleEvent_heartbeat(event)

        elif event.event in [events.EventCodes.resource.created, events.EventCodes.resource.destroyed]:
            self.updateTree()

        elif event.event in [events.EventCodes.resource.changed, events.EventCodes.resource.driver_loaded,
                             events.EventCodes.resource.driver_unloaded]:
            pass

    def handleEvent_heartbeat(self, event):
        # dlg = wx.MessageDialog(self, 'Heartbeat', 'Heartbeat', wx.OK|wx.ICON_INFORMATION)
        # dlg.ShowModal()
        # dlg.Destroy()
        pass