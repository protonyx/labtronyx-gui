import sys
import os
import logging
import importlib
import copy

import Tkinter as Tk

# import ImageTk
# from PIL import Image

sys.path.append("..")
from InstrumentManager import InstrumentManager
from LabManager import LabManager

from include import *



class Statusbar(Tk.Frame):
    """
    TODO:
    - Add sections
    """
    def __init__(self, master, sections=1):
        Tk.Frame.__init__(self, master)
        
        if sections < 1:
            sections = 1
                
        self.sections = [None] * sections
        for i in range(0, sections):
            self.sections[i] = Tk.Label(self, bd=1, relief=Tk.SUNKEN, anchor=Tk.W)
            self.sections[i].pack(fill=Tk.X)
            
    def add_section(self):
        pass

    def set(self, section, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self, section):
        self.label.config(text="")
        self.label.update_idletasks()
        
class Toolbar(Tk.Frame):
    def __init__(self, master, **kwargs):
        Tk.Frame.__init__(self, master)
            
class ResourceTree(Tk.Frame):
    
    validGroups = ['hostname', 'deviceType']
    
    # Tree Organization
    treeGroup = 'hostname'
    treeSort = 'deviceModel'
    
    def __init__(self, master, labManager):
        Tk.Frame.__init__(self, master)
        
        self.labManager = labManager
        
        Tk.Label(self, text='Instruments').pack(side=Tk.TOP)
        self.tree = ttk.Treeview(self, height=20)
        
        self.tree['columns'] = ('Type', 'Vendor', 'Model', 'Serial')
        self.tree.heading('#0', text='Instrument')
        self.tree.column('Vendor', width=80)
        self.tree.heading('Vendor', text='Vendor')
        self.tree.column('Model', width=80)
        self.tree.heading('Model', text='Model')
        self.tree.column('Type', width=100)
        self.tree.heading('Type', text='Type')
        self.tree.column('Serial', width=80)
        self.tree.heading('Serial', text='Serial Number')
        self.tree.pack(fill=Tk.BOTH)
        
        self.nodes = []
        self.resources = {}
        
        self.changeGrouping()
        
    def bind(self, sequence=None, func=None, add=None):
        return self.tree.bind(sequence, func, add)
    
    def identify_row(self, y):
        return self.tree.identify_row(y)
    
    def changeGrouping(self, group='hostname'):
        # Clear the treeview
        self._clear()
        self.treeGroup = group
        
        # Build a list of group values
        if self.treeGroup is 'hostname':
            # Fixes a bug where hosts were not added if no resources were present
            for gval in self.labManager.getConnectedHosts():
                self.tree.insert('', Tk.END, gval, text=gval, open=True)  # , image=img_host)
                
        elif self.treeGroup in self.validGroups:
            group_vals = []
            for res in resources:
                gv = res.get(self.treeGroup, None)
                if gv is not None and gv not in group_vals:
                    group_vals.append(gv)
            
            group_vals.sort()
            
            # Create group tree nodes
            for gval in group_vals:
                # TODO: Add images to treeview
                self.tree.insert('', Tk.END, gval, text=gval, open=True)
                
        self.refresh()
    
    def refresh(self, sort='deviceType', reverseOrder=False):
        """
        Sorting can be done on any valid key
        """
        # TODO: Get tree view images working
        # Import Image Assets
        # img_host = Image.open('assets/computer.png')
        # img_host = ImageTk.PhotoImage(img_host)
        # img_device = Image.open('assets/drive.png')
        # img_device = ImageTk.PhotoImage(img_device)
        
        self.labManager.refresh()
        
        self.resources = self.labManager.getProperties()

        # Get a flat list of resources and sort
        resources = self.resources
        resourceProperties = resources.values()
        resourceProperties.sort(key=lambda res: res.get(sort, ''), reverse=reverseOrder)
        
        # Populate child nodes
        for res in resourceProperties:
            lineID = res.get('uuid')
            group = res.get(self.treeGroup)
            text = res.get('resourceID', '')
            
            if lineID is not None and lineID not in self.nodes:
                self.tree.insert(group, Tk.END, lineID, text=text)  # , image=img_device)
                self.nodes.append(lineID)
            
            self.tree.set(lineID, 'Vendor', res.get('deviceVendor', ''))
            self.tree.set(lineID, 'Model', res.get('deviceModel', ''))
            self.tree.set(lineID, 'Type', res.get('deviceType', ''))
            self.tree.set(lineID, 'Serial', res.get('deviceSerial', ''))
            
        # Purge old nodes
        for res_uuid in self.nodes:
            if res_uuid not in resources:
                self.nodes.remove(res_uuid)
                self.tree.delete(res_uuid)
    
    def _clear(self):
        treenodes = self.tree.get_children()
        for n in treenodes:
            self.tree.delete(n)
            
        self.nodes = []
        
class TextHandler(logging.Handler):
    """ 
    Logging handler to direct logging input to a Tkinter Text widget
    """
    def __init__(self, console):
        logging.Handler.__init__(self)

        self.console = console

    def emit(self, record):
        message = self.format(record) + '\n'
        
        # Disabling states so no user can write in it
        self.console.configure(state=Tk.NORMAL)
        self.console.insert(Tk.END, message)
        self.console.configure(state=Tk.DISABLED)
        self.console.see(Tk.END)
        
if __name__ == "__main__":
    # Load Application GUI
    try:
        main_gui = a_Main()
        main_gui.mainloop()
         
    except Exception as e:
        print "Unable to load main application"
        raise
        sys.exit()
