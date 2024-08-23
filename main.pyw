# -*- coding: utf-8 -*-
"""
SuperDrive GUI
Created on Thu Aug 22 08:15:40 2024

@author: TOSmith
"""

import wx
from core import Listener

class MainFrame(wx.Frame):
    def __init__(self,overdrive_connection):
        super().__init__(parent=None,title="SuperDrive 1.0")
        self.SetIcon(wx.Icon('img/icon.ico'))
        self.overdrive_connection = overdrive_connection
        self.overdrive = Listener(self, self.overdrive_connection)
        self.Bind(wx.EVT_CLOSE,self.on_close)
        '''Init Layout'''
        self.panel_main = wx.Panel(self)
        self.sizer_main = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_secondary = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_preview = wx.BoxSizer(wx.VERTICAL)
        self.sizer_program = wx.BoxSizer(wx.VERTICAL)
        
        '''Control Widgets'''
        self.toggle_active = wx.Button(self.panel_main, label="Deactivate")
        self.toggle_active.Bind(wx.EVT_BUTTON,self.on_toggle)
        
        '''Preview Widgets'''
        self.label_preview_index = wx.StaticText(self.panel_main,label="")
        self.label_preview_slug = wx.StaticText(self.panel_main,label="")
        self.label_preview_shot_name = wx.StaticText(self.panel_main,label="")
        self.label_preview_template_name = wx.StaticText(self.panel_main,label="")
        self.label_preview_transition_name = wx.StaticText(self.panel_main,label="")
        
        '''Program Widgets'''
        self.label_program_index = wx.StaticText(self.panel_main,label="")
        self.label_program_slug = wx.StaticText(self.panel_main,label="")
        self.label_program_shot_name = wx.StaticText(self.panel_main,label="")
        self.label_program_template_name = wx.StaticText(self.panel_main,label="")
        self.label_program_transition_name = wx.StaticText(self.panel_main,label="")
        
        '''Filling Sizers'''
        self.sizer_preview.AddMany([(self.label_preview_index,1,wx.ALL|wx.CENTER),
                                    (self.label_preview_slug,1,wx.ALL|wx.CENTER),
                                    (self.label_preview_shot_name,1,wx.ALL|wx.CENTER),
                                    (self.label_preview_template_name,1,wx.ALL|wx.CENTER),
                                    (self.label_preview_transition_name,1,wx.ALL|wx.CENTER)])
        self.sizer_program.AddMany([(self.label_program_index,1,wx.ALL|wx.CENTER),
                                    (self.label_program_slug,1,wx.ALL|wx.CENTER),
                                    (self.label_program_shot_name,1,wx.ALL|wx.CENTER),
                                    (self.label_program_template_name,1,wx.ALL|wx.CENTER),
                                    (self.label_program_transition_name,1,wx.ALL|wx.CENTER)])
        self.sizer_secondary.AddMany([(self.sizer_preview,1,wx.ALL|wx.CENTER),
                                      (self.sizer_program,1,wx.ALL|wx.CENTER)])
        self.sizer_main.AddMany([(self.toggle_active,1,wx.ALL|wx.CENTER),
                                 (self.sizer_secondary,1,wx.ALL|wx.CENTER)])
        self.panel_main.SetSizerAndFit(self.sizer_main)
        self.SetInitialSize((450,100))
        self.SetMinSize((450,100))
        self.Layout()
        self.overdrive.start()
        self.Show()
        
    def on_close(self, event):
        self.overdrive.listening = False
        self.Destroy()
    
    def on_toggle(self, event):
        state = self.toggle_active.GetLabel()
        if state == "Deactivate":
            self.toggle_active.SetLabel("Activate")
            self.overdrive.listening = False
        else:
            self.toggle_active.SetLabel("Deactivate")
            self.overdrive = Listener(self, self.overdrive_connection)
            self.overdrive.start()
        
def main():
    app=[]; app = wx.App(None)
    frame = MainFrame(('10.10.78.10', 8760))
    app.SetTopWindow(frame)
    app.MainLoop()
        
if __name__ == "__main__":
    main()