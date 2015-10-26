import wx
import wx.gizmos

from labtronyx.common import events
from labtronyxgui.bases.wx_view import ViewBase

class MainApp(wx.App):
    pass

class MainView(ViewBase):

    def __init__(self, controller):
        wx.Frame.__init__(self, parent=None, id=-1, title="Labtronyx", size=(640, 480),
                          style=wx.DEFAULT_FRAME_STYLE)
        self._controller = controller
        self._controller.registerView(self)

        # self.sizer = wx.BoxSizer(wx.VERTICAL)
        # self.frame.SetSizer(self.sizer)

        # Build Menu
        self.buildMenubar()

        # Build Tree
        self.treePanel = wx.Panel(parent=self, id=wx.ID_ANY, style=wx.WANTS_CHARS)
        self.tree = wx.gizmos.TreeListCtrl(parent=self.treePanel, id=wx.ID_ANY,
                                pos=wx.DefaultPosition, size=wx.DefaultSize,
                                style=wx.TR_HAS_BUTTONS|wx.TR_HIDE_ROOT)
        self.buildTree()
        self.treePanel.Bind(wx.EVT_SIZE, self.e_OnSize)
        self.tree.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.e_OnRightClick)
        # self.tree.Bind(wx.EVT_KEY_UP, self.e_OnKeyEvent)

        # Event bindings
        self.Bind(wx.EVT_CLOSE, self.e_OnWindowClose)

        # self.tree.Expand(self.node_root)

        self.Show(True)

        self.SetSize((640, 480))
        # self.Fit()

        # Run updates
        wx.CallAfter(self.update_tree)

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
        self.tree.AddColumn('')
        self.tree.AddColumn('Type')
        self.tree.AddColumn('Vendor')
        self.tree.AddColumn('Model')
        self.tree.AddColumn('Serial')
        self.tree.SetMainColumn(0)
        self.tree.SetColumnWidth(0, 175)
        self.node_root = self.tree.AddRoot("Labtronyx") # Add hidden root item
        self.tree.SetPyData(self.node_root, None)
        self.nodes_hosts = {}
        self.nodes_resources = {}

    def update_tree(self):
        # Hosts
        for ip_address, host_controller in self._controller.hosts.items():
            # Add new hosts
            if ip_address not in self.nodes_hosts:
                hostname = self._controller.networkHostname(ip_address)

                child = self.tree.AppendItem(self.node_root, hostname)
                self.tree.SetPyData(child, ip_address)
                self.nodes_hosts[ip_address] = child

                self.tree.Expand(child)

            host_node = self.nodes_hosts.get(ip_address)

            # Resources
            for res_uuid, res_controller in host_controller.resources.items():
                # Add new resources
                if res_uuid not in self.nodes_resources:
                    res_prop = res_controller.properties

                    # Resource Name
                    node_name = res_prop.get('resourceID')

                    child = self.tree.AppendItem(host_node, node_name)
                    self.tree.SetPyData(child, res_uuid)
                    self.nodes_resources[res_uuid] = child

    # wx Events

    def e_OnRightClick(self, event):
        pos = event.GetPosition()
        item, flags, col = self.tree.HitTest(pos)

        if item:
            node_data = self.tree.GetPyData(item)

            if node_data in self._controller.hosts:
                # Host
                pass

            elif self._controller.get_resource(node_data) is not None:
                # Resource
                menu = wx.Menu()
                ctx_control = menu.Append(-1, "&Control", "Control")
                self.Bind(wx.EVT_MENU, lambda event: self.e_ResourceContextControl(event, node_data), ctx_control)
                menu.AppendSeparator()
                ctx_properties = menu.Append(-1, "&Properties", "Properties")
                self.Bind(wx.EVT_MENU, lambda event: self.e_ResourceContextProperties(event, node_data), ctx_properties)

                self.PopupMenu(menu, event.GetPosition())

    def e_ResourceContextControl(self, event, uuid):
        pass

    def e_ResourceContextProperties(self, event, uuid):
        pass

    def e_OnKeyEvent(self, event):
        keycode = event.GetKeyCode()
        pass

    def e_OnSize(self, event):
        w,h = self.GetClientSizeTuple()
        self.tree.SetDimensions(0, 0, w, h)

    def e_MenuExit(self, event):
        self.Close(True)

    def e_OnWindowClose(self, event):
        self.Destroy()

    # Controller Events

    def handleEvent(self, event):
        """
        Handle events from the controller. Assume invocation from outside GUI thread and call event handlers using
        wx.CallAfter

        :param event:
        :param args:
        :return:
        """
        if event == events.EventCodes.manager.heartbeat:
            wx.CallAfter(self.handleEvent_heartbeat, event)

        elif event == events.EventCodes.resource.created:
            wx.CallAfter(self.handleEvent_new_resource, event)

        elif event == events.EventCodes.resource.destroyed:
            wx.CallAfter(self.handleEvent_del_resource, event)

        elif event == events.EventCodes.driver.loaded:
            wx.CallAfter(self.handleEvent_driver_load, event)

        elif event == events.EventCodes.driver.unloaded:
            wx.CallAfter(self.handleEvent_driver_unload, event)

    def handleEvent_heartbeat(self, event):
        # dlg = wx.MessageDialog(self, 'Heartbeat', 'Heartbeat', wx.OK|wx.ICON_INFORMATION)
        # dlg.ShowModal()
        # dlg.Destroy()
        pass

    def handleEvent_new_resource(self, event):
        pass

    def handleEvent_del_resource(self, event):
        pass

    def handleEvent_driver_load(self, event):
        pass

    def handleEvent_driver_unload(self, event):
        pass