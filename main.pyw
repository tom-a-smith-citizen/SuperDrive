# -*- coding: utf-8 -*-
"""
SuperDrive GUI
Created on Thu Aug 22 08:15:40 2024

@author: TOSmith
"""

import wx #GUI
from core import Listener #Backend with FloorDirectorAPI
from ObjectListView import ObjectListView, ColumnDefn, OLVEvent #Data Presentation
import threading, time

class MainFrame(wx.Frame):
    def __init__(self,overdrive_connection):
        super().__init__(parent=None,title="SuperDrive 1.0.1")
        self.SetIcon(wx.Icon('img/icon.ico'))
        self.overdrive_connection = overdrive_connection
        self.overdrive = Listener(self, self.overdrive_connection)
        self.Bind(wx.EVT_CLOSE,self.on_close)
        '''Init Layout'''
        self.panel_main = wx.Panel(self)
        self.sizer_main = wx.FlexGridSizer(2,2,0,0)
        self.sizer_main.AddGrowableRow(1,1)
        self.sizer_main.AddGrowableCol(0,1)
        self.sizer_main.AddGrowableCol(1,1)
        self.statusbar = self.CreateStatusBar(2)
        
        '''Control Widgets'''
        self.label_control = wx.StaticText(self.panel_main,label="")
        
        '''Preview Widgets'''
        self.label_preview = wx.StaticText(self.panel_main, label="Prepared")
        self.olv_preview = ObjectListView(self.panel_main, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.EXPAND)
        
        '''Program Widgets'''
        self.label_program = wx.StaticText(self.panel_main, label="On Air")
        self.olv_program = ObjectListView(self.panel_main, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.EXPAND)
        
        '''Filling Sizers'''
        self.sizer_main.AddMany([(self.label_preview,1,wx.ALL|wx.CENTER),
                                 (self.label_program,1,wx.ALL|wx.CENTER),
                                 (self.olv_preview,1,wx.ALL|wx.EXPAND),
                                 (self.olv_program,1,wx.ALL|wx.EXPAND)])
        self.panel_main.SetSizerAndFit(self.sizer_main)
        self.SetInitialSize(self.GetBestSize()) 
        self.SetMinSize((450,100))
        self.Layout()
        self.overdrive.start()
        self.create_menu()
        self.Show()
    
    def set_columns(self):
        self.col_index = ColumnDefn("Page", "left", -1, "_index", isSpaceFilling=True)
        self.col_slug = ColumnDefn("Slug", "left", -1, "slug", isSpaceFilling=True)
        self.col_shot = ColumnDefn("Shot", "left", -1, "shot_name", isSpaceFilling=True)
        self.col_template = ColumnDefn("Template", "left", -1, "template_name", isSpaceFilling=True)
        self.col_transition = ColumnDefn("Transition", "left", -1, "transition_name", isSpaceFilling=True)
        self.olv_preview.SetColumns([self.col_index,
                                     self.col_slug,
                                     self.col_shot,
                                     self.col_template,
                                     self.col_transition])
        self.olv_program.SetColumns([self.col_index,
                                     self.col_slug,
                                     self.col_shot,
                                     self.col_template,
                                     self.col_transition])
        try:
            self.olv_preview.SetObjects(self.overdrive.prepared_olv)
        except Exception as e:
            print(e) 
        try:
            self.olv_program.SetObjects(self.overdrive.on_air_olv)
        except Exception as e:
            print(e)
    
    def on_close(self, event):
        self.overdrive.listening = False
        self.Destroy()
        
    def create_menu(self):
        menu_bar = wx.MenuBar()
            
        file_menu = wx.Menu()  
        active = file_menu.Append(wx.ID_ANY, 'Activate/Deactivate', 'Start or stop SuperDrive.')
        self.Bind(event=wx.EVT_MENU,handler=self.on_active,source=active)
        _quit = file_menu.Append(wx.ID_ANY, 'Quit', 'Quit SuperDrive.')
        self.Bind(event=wx.EVT_MENU,handler=self.on_quit,source=_quit)
        menu_bar.Append(file_menu, '&File')
        
        edit_menu = wx.Menu()
        settings = edit_menu.Append(wx.ID_ANY, 'Settings', 'Adjust settings')
        self.Bind(event=wx.EVT_MENU,handler=self.on_settings,source=settings)
        menu_bar.Append(edit_menu, '&Edit')
        
        help_menu = wx.Menu()
        about_option = help_menu.Append(wx.ID_ANY, 'About','Information about this program.')
        self.Bind(event=wx.EVT_MENU,handler=self.on_about,source=about_option)
        
        documentation_option = help_menu.Append(wx.ID_ANY, 'Documention',"Opens a PDF of this program's documentation.")
        self.Bind(event=wx.EVT_MENU,handler=self.on_documentation,source=documentation_option)
        
        menu_bar.Append(help_menu, '&Help')
        
        self.SetMenuBar(menu_bar)
        
    def on_active(self, event):
        if self.overdrive.listening:
            self.overdrive.listening = False
        else:
            self.overdrive = Listener(self, self.overdrive_connection)
            self.overdrive.start()
            
    def on_quit(self, event):
        dlg = wx.MessageDialog(self,'Are you sure you want to quit? Supers will no longer advance automatically.','Quit?',wx.YES_NO)
        result = dlg.ShowModal()
        if result == wx.ID_YES:
            self.on_close(wx.Event)
            
    def on_settings(self, event):
        pass
    
    def on_about(self, event):
        pass
    
    def on_documentation(self, event):
        pass
        
def main():
    app=[]; app = wx.App(None)
    frame = MainFrame(('10.10.78.10', 8760))
    app.SetTopWindow(frame)
    app.MainLoop()
        
if __name__ == "__main__":
    main()