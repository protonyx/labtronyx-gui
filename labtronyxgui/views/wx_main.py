import wx
import wx.gizmos

from labtronyx.common import events

class MainApp(wx.App):
    pass

class MainView(wx.Frame):

    def __init__(self, controller):
        wx.Frame.__init__(self, parent=None, id=-1, title="Labtronyx", size=(640, 480),
                          style=wx.DEFAULT_FRAME_STYLE)
        self._controller = controller

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

        # Event bindings
        self.Bind(wx.EVT_CLOSE, self.e_OnWindowClose)


        #
        # # Event handlers
        # Publisher().subscribe(self.handleEvent_new_resource, "event")

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
        all_hosts = self._controller.list_hosts()

        # Hosts
        for ip_address in all_hosts:
            # Add new hosts
            if ip_address not in self.nodes_hosts:
                hostname = self._controller.networkHostname(ip_address)

                child = self.tree.AppendItem(self.node_root, hostname)
                self.tree.SetPyData(child, ip_address)
                self.nodes_hosts[ip_address] = child

                self.tree.Expand(child)

            host_node = self.nodes_hosts.get(ip_address)

            # Resources
            for res_uuid in self._controller.list_resources(ip_address):
                # Add new resources
                if res_uuid not in self.nodes_resources:
                    res_prop = self._controller.get_resource_properties(res_uuid)

                    # Resource Name
                    node_name = res_prop.get('resourceID')

                    child = self.tree.AppendItem(host_node, node_name)
                    self.tree.SetPyData(child, res_uuid)
                    self.nodes_resources[res_uuid] = child

    # wx Events

    def e_OnSize(self, event):
        w,h = self.GetClientSizeTuple()
        self.tree.SetDimensions(0, 0, w, h)

    def e_MenuExit(self, event):
        self.Close(True)

    def e_OnWindowClose(self, event):
        self.Destroy()

    # Controller Events

    def handleEvent(self, event, args):
        """
        Handle events from the controller. Assume invocation from outside GUI thread and call event handlers using
        wx.CallAfter

        :param event:
        :param args:
        :return:
        """
        if event == events.ManagerEvents.heartbeat:
            wx.CallAfter(self.handleEvent_heartbeat, event, args)

        elif event == events.ResourceEvents.created:
            wx.CallAfter(self.handleEvent_new_resource, event, args)

        elif event == events.ResourceEvents.destroyed:
            wx.CallAfter(self.handleEvent_del_resource, event, args)

        elif event == events.ResourceEvents.driver_load:
            wx.CallAfter(self.handleEvent_driver_load, event, args)

        elif event == events.ResourceEvents.driver_unload:
            wx.CallAfter(self.handleEvent_driver_unload, event, args)

    def handleEvent_heartbeat(self, event, args):
        # dlg = wx.MessageDialog(self, 'Heartbeat', 'Heartbeat', wx.OK|wx.ICON_INFORMATION)
        # dlg.ShowModal()
        # dlg.Destroy()
        pass

    def handleEvent_new_resource(self, event, args):
        pass

    def handleEvent_del_resource(self, event, args):
        pass

    def handleEvent_driver_load(self, event, args):
        pass

    def handleEvent_driver_unload(self, event, args):
        pass