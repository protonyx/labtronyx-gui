__author__ = 'kkennedy'

import sys
import os
import logging
import importlib

import Tkinter as Tk
import ttk
import tkMessageBox

class MainView(Tk.Tk):
    """
    Main application for
    TODO:
    - Splash screen on load (http://code.activestate.com/recipes/534124-elegant-tkinter-splash-screen/)
    - Toolbar (http://zetcode.com/gui/tkinter/menustoolbars/)
    - Instrument Nicknames
    - Persistant settings
    - Nanny thread to periodically check if connected hosts and resources are still active
    """
    applets = {}  # Module name -> View info
    openApplets = {}

    def __init__(self, master=None):
        Tk.Tk.__init__(self, master)

        # Get root directory
        # Get the root path
        can_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir)  # Resolves symbolic links
        self.rootPath = os.path.abspath(can_path)

        # Instantiate a logger
        self.logger = logging.getLogger(__name__)
        self.logFormatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
        self.logger.setLevel(logging.DEBUG)
        # TODO: Log to console?
        #console = logging.StreamHandler(stream=sys.stdout)
        #self.logger.addHandler(console)
        # TODO: Log to file?

        # Load applets
        import applets
        self.applets = applets.getAllApplets()

        for applet in self.applets.keys():
            self.logger.debug("Found Applet: %s", applet)

        # Instantiate a LabManager
        import socket
        localhost = socket.gethostname()

        self.lab = LabManager()
        if not self.lab.addManager(localhost):
            # Instantiate a local InstrumentManager object
            self.local_manager = InstrumentManager()
            self.local_manager.start()
            self.lab.addManager(localhost)

        # Register new resource callback on local manager
        man = self.lab.getManager(localhost)
        if man is not None:
            man._registerCallback('event_new_resource', lambda: self.cb_event_new_resource())

        # GUI Startup
        self.rebuild()
        self.rebind()

        # TODO: Persistent Settings

        self.process_notifications()

    def rebuild(self):
        """
        Rebuilds all GUI elements and positions

        Pane Layout:
        +-----------------------------------+
        |                                   |
        |                                   |
        |            tree frame             |
        |                                   |
        |                                   |
        +-----------------------------------+
        |                                   |
        |             logFrame              |
        |                                   |
        +-----------------------------------+
        """
        self.wm_title("Labtronyx Instrument Control and Automation")
        self.minsize(500, 500)
        self.geometry("800x600")

        #=======================================================================
        # Menubar
        #=======================================================================
        self.option_add('*tearOff', Tk.FALSE)
        self.menubar = Tk.Menu(self)
        self['menu'] = self.menubar
        # File
        self.m_File = Tk.Menu(self.menubar)
        self.menubar.add_cascade(menu=self.m_File, label='File')
        self.m_File.add_command(label='Connect to host...', command=lambda: self.cb_managerConnect())
        self.m_File.add_command(label='Refresh all hosts...', command=lambda: self.cb_refreshTree())
        self.m_File.add_separator()
        # File - LogLevel
        self.m_File_LogLevel = Tk.Menu(self.m_File)
        self.m_File.add_cascade(menu=self.m_File_LogLevel, label='Log Level')
        self.m_File_LogLevel.add_radiobutton(label='Critical', command=lambda: self.cb_setLogLevel(logging.CRITICAL))
        self.m_File_LogLevel.add_radiobutton(label='Error', command=lambda: self.cb_setLogLevel(logging.ERROR))
        self.m_File_LogLevel.add_radiobutton(label='Warning', command=lambda: self.cb_setLogLevel(logging.WARNING))
        self.m_File_LogLevel.add_radiobutton(label='Info', command=lambda: self.cb_setLogLevel(logging.INFO))
        self.m_File_LogLevel.add_radiobutton(label='Debug', command=lambda: self.cb_setLogLevel(logging.DEBUG))

        self.m_File.add_separator()
        self.m_File.add_command(label='Exit', command=self.cb_exitWindow)
        # Help
        self.m_Help = Tk.Menu(self.menubar, name='help')
        self.menubar.add_cascade(menu=self.m_Help, label='Help')
        self.m_Help.add_command(label='About')

        #=======================================================================
        # Status Bar
        #=======================================================================
        self.statusbar = Statusbar(self)
        self.statusbar.pack(side=Tk.BOTTOM, fill=Tk.X)

        # Horizontal Pane
        self.HPane = Tk.PanedWindow(self, orient=Tk.VERTICAL, height=400, sashpad=5, sashwidth=8)
        self.HPane.pack(fill=Tk.BOTH, expand=Tk.YES, padx=5, pady=5)
        #=======================================================================
        # Horizontal Pane - Top
        #=======================================================================
        # Vertical Pane
        #=======================================================================
        # self.VPane = Tk.PanedWindow(self.HPane, orient=Tk.HORIZONTAL, height=400, width=400, sashpad=5, sashwidth=8)
        # self.HPane.add(self.VPane)
        #=======================================================================

        #=======================================================================
        #     Vertical Pane - Left
        #     Treeview Frame
        #     Min size: 400px
        #=======================================================================
        self.treeFrame = ResourceTree(self.HPane, self.lab)  # , highlightcolor='green', highlightthickness=2)
        # self.VPane.add(self.treeFrame, width=800, minsize=400)
        self.HPane.add(self.treeFrame, width=600, minsize=400)

        #=======================================================================
        #     Vertical Pane - Right
        #     Controls Frame
        #     Min size: None
        #=======================================================================
        #=======================================================================
        # self.controlFrame = Tk.Frame(self.VPane)
        # self.VPane.add(self.controlFrame)
        #=======================================================================

        # TODO: Add some controls here
        # Notebook?: http://www.tkdocs.com/tutorial/complex.html
        #=======================================================================
        # Horizontal Pane - Bottom
        # Logger Frame
        # Min size: 200px
        #=======================================================================
        self.logFrame = Tk.Frame(self.HPane)
        self.HPane.add(self.logFrame, width=200, minsize=200)

        Tk.Label(self.logFrame, text='Log').pack(side=Tk.TOP)
        self.logConsole = Tk.Text(self.logFrame)
        self.logConsole.configure(state=Tk.DISABLED)
        self.logConsole.pack(fill=Tk.BOTH)

    def rebind(self):
        """
        Creates all of the GUI element bindings
        """
        self.wm_protocol("WM_DELETE_WINDOW", self.cb_exitWindow)

        # Bind Right Click
        if sys.platform.startswith('darwin'):
            # OS X
            self.treeFrame.bind('<Button-2>', self.e_TreeRightClick)
        else:
            # Windows, Linux
            self.treeFrame.bind('<Button-3>', self.e_TreeRightClick)

        # Bind Double Click
        self.treeFrame.bind('<Double-Button-1>', self.e_TreeDoubleClick)

        # Console
        h_textHandler = TextHandler(self.logConsole)
        h_textHandler.setFormatter(self.logFormatter)
        self.logger.addHandler(h_textHandler)

    #===========================================================================
    # Callback Functions
    #
    # Callback functions with variable parameters should:
    # - start with 'cb_'
    #===========================================================================
    def cb_exitWindow(self):
        try:
            if tkMessageBox.askokcancel("Quit", "Do you really wish to quit?"):
                if hasattr(self, 'local_manager'):
                    self.local_manager.stop()
                self.destroy()

        except:
            self.destroy()

    def cb_setLogLevel(self, level):
        # numeric_level = getattr(logging, loglevel.upper(), None)
        self.logger.setLevel(level)
        self.logger.log(level, 'Log Level Changed')

    def cb_managerConnect(self):
        # Spawn a window to get address and port

        # Create the child window
        w_connectToHost = ManagerPages.a_ConnectToHost(self, lambda address, port: self.cb_addManager(address, port))

    def cb_addManager(self, address, port=None):
        # Attempt a connection to the manager
        if not self.lab.addManager(address, port):
            tkMessageBox.showwarning('Operation Failed',
                                     'Unable to connect to InstrumentManager')

        self.cb_refreshTree()

    def cb_managerDisconnect(self, address):
        self.lab.removeManager(address)

        self.cb_refreshTree()

    def cb_managerShutdown(self, address):
        man = self.lab.getManager(address)
        man.stop()
        self.lab.removeManager(address)

        self.cb_refreshTree()

    def cb_addResource(self, address):
        man = self.lab.getManager(address)
        interfaces = man.getInterfaces()

        # Create the child window
        w_addResource = ManagerPages.a_AddResource(self, self, interfaces, lambda interface, resID: man.addResource(interface, resID))

        # Make the child modal
        w_addResource.focus_set()
        w_addResource.grab_set()

    def cb_refreshTree(self, address=None):
        self.lab.refresh()

        self.treeFrame.refresh()

    def cb_loadApplet(self, uuid, applet=None):
        if applet is not None:
            try:
                # Check if the specified model is valid
                testModule = importlib.import_module(applet)
                reload(testModule)  # Reload the module in case anything has changed

                className = applet.split('.')[-1]
                testClass = getattr(testModule, className)

                instrument = self.lab.getInstrument(uuid)

                if instrument is not None:
                    appletInst = testClass(self, instrument)

                    # Store the object in open views
                    self.openApplets[uuid] = appletInst

                    appletInst.run()

                else:
                    tkMessageBox.showwarning('Unable to load applet', 'Unable to get a handle for the resource')

            except Exception as e:
                tkMessageBox.showerror(e.__class__.__name__, e.message)

        else:
            # Check if a view is already open
            if uuid in self.openApplets.keys():
                try:
                    # Do nothing? Bring window into focus?
                    appletInst = self.openApplets.get(uuid)

                    appletInst.lift()

                    return None
                except:
                    # On exception, load the view selector
                    pass

            # Find compatible views
            res = self.lab.getResource(uuid)
            properties = res.getProperties()

            driverName = properties.get('driver')
            validApplets = []

            # Find a view with a compatible model
            for appletModule, appletInfo in self.applets.items():
                if driverName in appletInfo.get('validDrivers', []):
                    validApplets.append(appletModule)

            # Find a generic view for this resource type
            resType = properties.get('resourceType')
            for appletModule, appletInfo in self.applets.items():
                if resType in appletInfo.get('validResourceTypes', []):
                    validApplets.append(appletModule)

            # Load the view
            if len(validApplets) > 1:
                # Load view selector if more than one found

                # Create the child window
                w_AppletSelector = ResourcePages.a_AppletSelector(self, validApplets, lambda appletModule: self.cb_loadApplet(uuid, appletModule))

            elif len(validApplets) == 1 and validApplets[0] is not None:
                # Load the view
                self.cb_loadApplet(uuid, validApplets[0])

            else:
                tkMessageBox.showwarning('Unable to load applet', 'No suitable applets could be found for this resource')

    def cb_loadDriver(self, uuid):
        try:
            dev = self.lab.getResource(uuid)

            # Spawn a window to select the driver to load
            w_DriverSelector = ResourcePages.a_LoadDriver(self, self.lab, uuid, self.cb_refreshTree)

            self.lab.refreshResource(uuid)

        except Exception as e:
            tkMessageBox.showerror(e.__class__.__name__, e.message)

        self.treeFrame.refresh()

    def cb_unloadDriver(self, uuid):
        try:
            dev = self.lab.getResource(uuid)
            dev.unloadDriver()
            self.lab.refreshResource(uuid)

        except Exception as e:
            tkMessageBox.showerror(e.__class__.__name__, e.message)

        self.treeFrame.refresh()

    def cb_configResource(self, uuid):
        try:
            dev = self.lab.getResource(uuid)

            prop = dev.getProperties()
            type = prop.get('resourceType')

            if hasattr(ConfigPages, 'config_%s' % type):
                config_class = getattr(ConfigPages, 'config_%s' % type)
                w_ConfigWindow = config_class(self, dev)

            else:
                tkMessageBox.showwarning('Resource Error', 'This resource has no configuration options')

        except Exception as e:
            tkMessageBox.showerror(e.__class__.__name__, e.message)

    def cb_ResourceProperties(self, uuid):
        try:
            dev = self.lab.getResource(uuid)
            w_ResourceProperties = ResourcePages.a_PropertyWindow(self, dev)

        except Exception as e:
            tkMessageBox.showerror(e.__class__.__name__, e.message)

    #===========================================================================
    # Notification Event Handlers
    #===========================================================================

    def process_notifications(self):
        managers = self.lab.getManager()

        for addresss, man in managers.items():
            man._checkNotifications()

        self.after(1000, self.process_notifications)

    def cb_event_new_resource(self):
        return self.cb_refreshTree()

    #===========================================================================
    # Event Handlers
    #
    # All Tk bound event handlers should:
    # - start with 'e_'
    # - accept a parameter 'event'
    #
    #===========================================================================

    def e_TreeRightClick(self, event):
        elem = self.treeFrame.identify_row(event.y)

        # Create a context menu
        menu = Tk.Menu(self)

        resources = self.lab.getProperties()
        hosts = self.lab.getConnectedHosts()

        # Populate menu based on context
        if elem in hosts:
            # Context is Hostname

            # Context menu:
            # -Refresh
            # -Load Device
            # -Get log?
            menu.add_command(label='Add Resource...',
                             command=lambda: self.cb_addResource(elem))
            menu.add_command(label='Refresh',
                             command=lambda: self.cb_refreshTree(elem))
            menu.add_command(label='Disconnect',
                             command=lambda: self.cb_managerDisconnect(elem))
            menu.add_command(label='Shutdown',
                             command=lambda: self.cb_managerShutdown(elem))

        elif elem in resources.keys():
            # Context is Resource, elem is the UUID

            # Context menu:
            # -Load Driver/Unload Driver
            # -Control Instrument (Launch View/GUI)
            res_props = resources.get(elem)

            menu.add_command(label='Control Device...', command=lambda: self.cb_loadApplet(elem))

            if res_props.get('driver', None) == None:
                menu.add_command(label='Load Driver...', command=lambda: self.cb_loadDriver(elem))
            else:
                menu.add_command(label='Unload Driver', command=lambda: self.cb_unloadDriver(elem))

            type = res_props.get('resourceType')
            if hasattr(ConfigPages, 'config_%s' % type):
                menu.add_command(label='Configure...', command=lambda: self.cb_configResource(elem))

            menu.add_separator()
            menu.add_command(label='Properties...', command=lambda: self.cb_ResourceProperties(elem))

        else:
            # Something else maybe empty space?
            menu.add_command(label='Connect to host...', command=lambda: self.cb_managerConnect())

        menu.post(event.x_root, event.y_root)

    def e_TreeDoubleClick(self, event):
        pass