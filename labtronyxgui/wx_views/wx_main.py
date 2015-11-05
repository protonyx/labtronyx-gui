import wx
import wx.aui
import wx.gizmos

from labtronyx.common import events
from . import FrameViewBase, PanelViewBase

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
        self.tree = wx.TreeCtrl(self.pnl_left, -1,
                                style=wx.TR_HAS_BUTTONS|wx.TR_HIDE_ROOT)
        self.host = wx.Choice(self.pnl_left, -1, style=wx.CB_SORT)
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
        self.pnl_content = wx.Panel(self.mainPanel)

        # Build Log
        self.log = wx.TextCtrl(self.mainPanel, -1, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)

        # Event bindings
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

        # Run updates
        wx.CallAfter(self.updateHostSelector)
        wx.CallAfter(self.updateTree)

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

        self.pnode_resources = self.tree.AppendItem(self.pnode_root, 'Resources')
        self.tree.SetItemImage(self.pnode_resources, self.art_resource)

        self.nodes_resources = {}

        # self.tree.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.e_OnRightClick)
        self.tree.Bind(wx.EVT_LEFT_DOWN, self.e_OnTreeLeftClick)

    def updateHostSelector(self):
        choices = [hcon.hostname for hcon in self.controller.hosts.values()]

        self.host.Clear()
        self.host.AppendItems(choices)

    def updateTree(self):
        # Hosts
        for ip_address, host_controller in self.controller.hosts.items():
            # Resources
            for res_uuid, res_controller in host_controller.resources.items():
                # Add new resources
                if res_uuid not in self.nodes_resources:
                    res_prop = res_controller.properties

                    # Resource Name
                    node_name = res_prop.get('resourceID')

                    child = self.tree.AppendItem(self.pnode_resources, node_name)
                    self.tree.SetPyData(child, res_uuid)
                    self.tree.SetItemImage(child, self.art_resource)
                    self.nodes_resources[res_uuid] = child

        # self.update_tree_columns()

    def e_MenuExit(self, event):
        self.Close(True)

    def e_OnWindowClose(self, event):
        self.Destroy()

    def e_OnTreeLeftClick(self, event):
        pos = event.GetPosition()
        item, flags = self.tree.HitTest(pos)

        if item == self.tree.GetSelection():
            pass

    def _handleEvent(self, event):
        if event.event == events.EventCodes.manager.heartbeat:
            self.handleEvent_heartbeat(event)

        elif event.event in [events.EventCodes.resource.created, events.EventCodes.resource.destroyed]:
            self.updateTree()

        elif event.event in [events.EventCodes.resource.changed, events.EventCodes.resource.driver_loaded,
                             events.EventCodes.resource.driver_unloaded]:
            self.update_tree_columns()

    def handleEvent_heartbeat(self, event):
        # dlg = wx.MessageDialog(self, 'Heartbeat', 'Heartbeat', wx.OK|wx.ICON_INFORMATION)
        # dlg.ShowModal()
        # dlg.Destroy()
        pass


class ResourceTreePanel(PanelViewBase):
    def __init__(self, parent, controller):
        super(ResourceTreePanel, self).__init__(parent, controller)

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)

        # Build Tree
        self.tree = wx.gizmos.TreeListCtrl(self, wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                                           style=wx.TR_HAS_BUTTONS|wx.TR_HIDE_ROOT)





    def update_tree_columns(self):
        for res_uuid, res_node in self.nodes_resources.items():
            res_con = self.controller.get_resource(res_uuid)

            if res_con is not None:
                res_props = res_con.properties
                self.tree.SetItemText(res_node, res_props.get('deviceType', ''), 1)
                self.tree.SetItemText(res_node, res_props.get('deviceVendor', ''), 2)
                self.tree.SetItemText(res_node, res_props.get('deviceModel', ''), 3)
                self.tree.SetItemText(res_node, res_props.get('deviceSerial', ''), 4)





    def e_OnTreeRightClick(self, event):
        pos = event.GetPosition()
        item, flags, col = self.tree.HitTest(pos)

        if item:
            node_data = self.tree.GetPyData(item)

            if node_data in self.controller.hosts:
                # Host
                pass

            elif self.controller.get_resource(node_data) is not None:
                # Resource
                menu = wx.Menu()
                ctx_control = menu.Append(-1, "&Control", "Control")
                self.Bind(wx.EVT_MENU, lambda event: self.e_ResourceContextControl(event, node_data), ctx_control)
                menu.AppendSeparator()
                ctx_properties = menu.Append(-1, "&Properties", "Properties")
                self.Bind(wx.EVT_MENU, lambda event: self.e_ResourceContextProperties(event, node_data), ctx_properties)

                self.PopupMenu(menu, event.GetPosition())

    def e_ResourceContextControl(self, event, uuid):
        from .wx_resources import ResourceControlView

        # Get the resource controller
        res_controller = self.controller.get_resource(uuid)

        # Instantiate and show the window
        win = ResourceControlView(self, res_controller)
        win.Show()

    def e_ResourceContextProperties(self, event, uuid):
        from .wx_resources import ResourcePropertiesView

        # Get the resource controller
        res_controller = self.controller.get_resource(uuid)

        # Instantiate and show the window
        win = ResourcePropertiesView(self, res_controller)
        win.Show()