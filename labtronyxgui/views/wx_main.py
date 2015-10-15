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

        # Add items?
        for x in range(5):
            child = self.tree.AppendItem(self.node_root, "Item %d" % x)
            self.tree.SetPyData(child, x)

            for y in range(5):
                subchild = self.tree.AppendItem(child, "Subitem %d" % y)
                self.tree.SetPyData(subchild, y)

        # self.tree.Expand(self.node_root)

        self.frame.Show(True)

        self.frame.SetSize((640, 480))
        # self.frame.Fit()

    def e_OnSize(self, event):
        w,h = self.frame.GetClientSizeTuple()
        self.tree.SetDimensions(0, 0, w, h)

    def e_MenuExit(self, event):
        self.frame.Close(True)

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