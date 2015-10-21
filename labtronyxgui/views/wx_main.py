import wx
import wx.gizmos

class MainView(object):

    def __init__(self, controller):
        self._controller = controller

        self.frame = wx.Frame(parent=None, id=-1,
                              title="Labtronyx",
                              size=(640, 480),
                              style=wx.DEFAULT_FRAME_STYLE)
        # self.sizer = wx.BoxSizer(wx.VERTICAL)
        # self.frame.SetSizer(self.sizer)

        # Build Menubar
        self.menubar = wx.MenuBar()
        self.menu_file = wx.Menu()
        item = self.menu_file.Append(-1, "E&xit\tCtrl-Q", "Exit")
        self.frame.Bind(wx.EVT_MENU, self.e_MenuExit, item)
        self.menubar.Append(self.menu_file, "&File")
        self.frame.SetMenuBar(self.menubar)

        self.panel = wx.Panel(parent=self.frame, id=wx.ID_ANY,
                              style=wx.WANTS_CHARS)
        self.panel.Bind(wx.EVT_SIZE, self.e_OnSize)

        # Build frame
        self.tree = wx.gizmos.TreeListCtrl(parent=self.panel, id=wx.ID_ANY,
                                pos=wx.DefaultPosition, size=wx.DefaultSize,
                                style=wx.TR_HAS_BUTTONS|wx.TR_HIDE_ROOT)
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

        # Add items?
        for x in range(5):
            child = self.tree.AppendItem(self.node_root, "Item %d" % x)
            self.tree.SetPyData(child, x)

            for y in range(5):
                subchild = self.tree.AppendItem(child, "Subitem %d" % y)
                self.tree.SetPyData(subchild, y)

        # Update tree
        self.update_tree()

        # self.tree.Expand(self.node_root)

        self.frame.Show(True)

        self.frame.SetSize((640, 480))
        # self.frame.Fit()

    def e_OnSize(self, event):
        w,h = self.frame.GetClientSizeTuple()
        self.tree.SetDimensions(0, 0, w, h)

    def e_MenuExit(self, event):
        self.frame.Close(True)

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

    def handle_event(self, event, *args):
        pass

    # Controller Events

    def event_new_host(self, event, *args):
        pass

    def event_del_host(self, event, *args):
        pass

    def event_new_resource(self, event, *args):
        pass

    def event_del_resource(self, event, *args):
        pass