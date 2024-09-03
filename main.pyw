# -*- coding: utf-8 -*-
"""
SuperDrive GUI
Created on Thu Aug 22 08:15:40 2024

@author: TOSmith
"""

import wx #GUI
from core import Listener #Backend with FloorDirectorAPI
from ObjectListView import FastObjectListView, ObjectListView, ColumnDefn #Data Presentation
import keyboard, pickle, os #Stroke capture, data persistence, file checking
import webbrowser #Open documentation
import logging

class MainFrame(wx.Frame):
    def __init__(self,overdrive_connection,superdrive_port,super_keyword,advance_key, press_delay, log, log_level):
        super().__init__(parent=None,title="SuperDrive")
        self.title = "SuperDrive 1.0.3"
        self.SetTitle(self.title)
        self.SetIcon(wx.Icon('img/icon.ico'))
        self.overdrive_connection = overdrive_connection
        self.superdrive_port = superdrive_port
        self.super_keyword = super_keyword
        self.advance_key = advance_key
        self.overdrive = Listener(self, self.overdrive_connection, self.super_keyword, self.advance_key)
        self.press_delay = press_delay #Seconds to wait before triggering the take and prepare.
        self.log = log
        self.log_level = log_level
        logging.basicConfig(filename='SuperDrive.log',level=self.log_level)
        #self.receiver = Receiver(self)
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
        self.olv_preview = FastObjectListView(self.panel_main, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.EXPAND)
        self.olv_preview.cellEditMode = FastObjectListView.CELLEDIT_NONE
        self.olv_preview.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)
        
        '''Program Widgets'''
        self.label_program = wx.StaticText(self.panel_main, label="On Air")
        self.olv_program = FastObjectListView(self.panel_main, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.EXPAND)
        self.olv_program.cellEditMode = FastObjectListView.CELLEDIT_NONE
        self.olv_program.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)
        
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
        #self.receiver.start()
        self.create_menu()
        self.Show()
    
    def on_key_down(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_SPACE:
            pass
        else:
            event.Skip()
    
    def set_columns(self):
        self.col_index = ColumnDefn("Page", "left", -1, "_index", isSpaceFilling=True)
        self.col_slug = ColumnDefn("Slug", "left", -1, "slug", isSpaceFilling=True)
        self.col_shot = ColumnDefn("Shot", "left", -1, "shot_name", isSpaceFilling=True)
        self.col_template = ColumnDefn("Template", "left", -1, "template_name", isSpaceFilling=True)
        self.col_transition = ColumnDefn("Transition", "left", -1, "transition_name", isSpaceFilling=True)
        self.col_is_super = ColumnDefn("Super", "left", -1, "is_super", isSpaceFilling=True)
        self.olv_preview.SetColumns([self.col_index,
                                     self.col_slug,
                                     self.col_shot,
                                     self.col_template,
                                     self.col_transition,
                                     self.col_is_super])
        self.olv_program.SetColumns([self.col_index,
                                     self.col_slug,
                                     self.col_shot,
                                     self.col_template,
                                     self.col_transition,
                                     self.col_is_super])
        try:
            self.olv_preview.SetObjects(self.overdrive.prepared_olv)
        except Exception as e:
            print(e) 
        try:
            self.olv_program.SetObjects(self.overdrive.on_air_olv)
        except Exception as e:
            print(e)
    
    def on_close(self, event):
        dlg = wx.MessageDialog(self,'Are you sure you want to quit SuperDrive?','Quit?',style=wx.YES_NO)
        result = dlg.ShowModal()
        if result == wx.ID_YES:
            self.overdrive.listening = False
            if hasattr(self, 'receiver'):
                self.receiver.receiving = False
            with open('settings.pkl','wb') as file:
                settings = [self.overdrive_connection,
                            self.superdrive_port,
                            self.super_keyword,
                            self.advance_key,
                            self.press_delay,
                            self.log_level]
                pickle.dump(settings,file)
                file.close()
            self.Destroy()
        
    def create_menu(self):
        menu_bar = wx.MenuBar()
            
        file_menu = wx.Menu()  
        active = file_menu.Append(wx.ID_ANY, 'Activate/Deactivate', 'Start or stop SuperDrive.')
        self.Bind(event=wx.EVT_MENU,handler=self.on_active,source=active)
        _quit = file_menu.Append(wx.ID_ANY, 'Quit', 'Quit SuperDrive.')
        self.Bind(event=wx.EVT_MENU,handler=self.on_close,source=_quit)
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
            self.overdrive = Listener(self, self.overdrive_connection, self.super_keyword, self.advance_key)
            self.overdrive.start()
    
    def on_remote_start(self):
        self.overdrive.listening = False
        self.overdrive = Listener(self, self.overdrive_connection, self.super_keyword, self.advance_key)
        self.overdrive.start()     
    
    def on_settings(self, event):
        SettingsFrame(self)
    
    def on_about(self, event):
        AboutFrame(self)
    
    def on_documentation(self, event):
        path = os.getcwd()
        webbrowser.open(f'{path}\\documentation\\documentation.pdf')
    
class SettingsFrame(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent=parent, title="SuperDrive Settings")
        self.parent = parent
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
        '''Init UI'''
        self.SetTitle(f'{self.parent.title} - Settings')
        self.SetIcon(wx.Icon('img/icon.ico'))
        self.parent = parent
        self.panel_main = wx.Panel(self)
        self.sizer = wx.FlexGridSizer(8,2,10,10)
        self.sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.log_levels = {"None": logging.NOTSET,
                           "Debug": logging.DEBUG,
                           "Info": logging.INFO,
                           "Warning": logging.WARNING,
                           "Error": logging.ERROR,
                           "Critical": logging.CRITICAL}
        self.log_choices = []
        for key in self.log_levels.keys():
            self.log_choices.append(key)
        
        '''Widgets'''
        self.label_key = wx.StaticText(self.panel_main,label="OverDrive Advance Key")
        self.button_key = wx.ToggleButton(self.panel_main, label="Assign Key")
        self.button_key.SetLabel(self.parent.advance_key)
        self.assigned = self.parent.advance_key
        self.button_key.Bind(wx.EVT_TOGGLEBUTTON, self.assign_key)
        self.button_key.Bind(wx.EVT_KEY_UP, self.get_key)
        
        self.label_overdrive_ip = wx.StaticText(self.panel_main,label="OverDrive Server IP")
        self.field_overdrive_ip = wx.TextCtrl(self.panel_main)
        self.field_overdrive_ip.SetValue(self.parent.overdrive.OverDrive_IP)
        
        self.label_overdrive_port = wx.StaticText(self.panel_main,label="OverDrive Port")
        self.field_overdrive_port = wx.TextCtrl(self.panel_main)
        self.field_overdrive_port.SetValue(str(self.parent.overdrive.OverDrive_port))
        
        self.label_superdrive_port = wx.StaticText(self.panel_main,label="SuperDrive Port")
        self.field_superdrive_port = wx.TextCtrl(self.panel_main)
        self.field_superdrive_port.SetValue(str(self.parent.superdrive_port))
        
        self.label_super_keyword = wx.StaticText(self.panel_main,label="Super Keyword")
        self.field_super_keyword = wx.TextCtrl(self.panel_main)
        self.field_super_keyword.SetValue(self.parent.overdrive.super_keyword)
        
        self.label_press_delay = wx.StaticText(self.panel_main,label="Advance Delay (Seconds)")
        self.field_press_delay = wx.TextCtrl(self.panel_main)
        self.field_press_delay.SetValue(str(self.parent.press_delay))
        self.spinner_press_delay = wx.SpinButton(self.panel_main)
        self.spinner_press_delay.Bind(wx.EVT_SPIN_UP, self.spinner_up)
        self.spinner_press_delay.Bind(wx.EVT_SPIN_DOWN, self.spinner_down)
        self.sizer_press_delay = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_press_delay.AddMany([(self.field_press_delay,1,wx.ALL|wx.CENTER),
                                        (self.spinner_press_delay,1,wx.ALL|wx.CENTER)])
        
        self.label_log_level = wx.StaticText(self.panel_main,label="Logging")
        self.choice_log_level = wx.Choice(self.panel_main,choices=self.log_choices)
        current_level = logging.getLogger().getEffectiveLevel()
        for key, value in self.log_levels.items():
            if value == current_level:
                n = list(self.log_levels.keys()).index(key)
                self.choice_log_level.SetSelection(n)
        
        self.button_apply = wx.Button(self.panel_main,label="Apply")
        self.button_apply.Bind(wx.EVT_BUTTON, self.on_apply)
        self.button_cancel = wx.Button(self.panel_main,label="Cancel")
        self.button_cancel.Bind(wx.EVT_BUTTON, self.on_cancel)
        
        '''Filling Sizers'''
        self.sizer_buttons.AddMany([(self.button_apply,1,wx.ALL|wx.CENTER),
                                    (self.button_cancel,1,wx.ALL|wx.CENTER)])
        self.sizer.AddMany([(self.label_key,1,wx.ALL|wx.CENTER),
                            (self.button_key,1,wx.ALL|wx.CENTER),
                            (self.label_overdrive_ip,1,wx.ALL|wx.CENTER),
                            (self.field_overdrive_ip,1,wx.ALL|wx.CENTER),
                            (self.label_overdrive_port,1,wx.ALL|wx.CENTER),
                            (self.field_overdrive_port,1,wx.ALL|wx.CENTER),
                            (self.label_superdrive_port,1,wx.ALL|wx.CENTER),
                            (self.field_superdrive_port,1,wx.ALL|wx.CENTER),
                            (self.label_super_keyword,1,wx.ALL|wx.CENTER),
                            (self.field_super_keyword,1,wx.ALL|wx.CENTER),
                            (self.label_press_delay,1,wx.ALL|wx.CENTER),
                            (self.sizer_press_delay,1,wx.ALL|wx.CENTER),
                            (self.label_log_level,1,wx.ALL|wx.CENTER),
                            (self.choice_log_level,1,wx.ALL|wx.CENTER),
                            (self.sizer_buttons,1,wx.ALL|wx.CENTER)])
        self.panel_main.SetSizerAndFit(self.sizer)
        self.SetInitialSize(self.GetBestSize())
        self.Layout()
        self.Show()
        
    def get_key(self, event):
        if self.button_key.GetValue() == True:
            self.assigned = keyboard.read_key()
            self.button_key.SetLabel(str(self.assigned))
            self.button_key.SetValue(False)
            self.panel_main.SetFocus()
            print(f'Assigned {self.assigned} as key.')
    
    def assign_key(self, event):
        self.panel_main.SetFocus()
        if hasattr(self, 'assigned'):
            del(self.assigned)
        self.button_key.SetValue(True)
        self.button_key.SetLabel("[[Press any key.]]")
    
    def spinner_down(self, event):
        current = float(self.field_press_delay.GetValue())
        current -= 0.25
        self.field_press_delay.SetValue(str(current))
        
    def spinner_up(self, event):
        current = float(self.field_press_delay.GetValue())
        current += 0.25
        self.field_press_delay.SetValue(str(current))
    
    def on_close(self, event):
        dlg = wx.MessageDialog(self,'Quit without saving your changes?','Quit?',wx.YES_NO)
        result = dlg.ShowModal()
        if result == wx.ID_YES:
            self.Destroy()
            
    def on_cancel(self, event):
        self.Destroy()
        
    def on_apply(self, event):
        if hasattr(self, 'assigned'):
            self.parent.overdrive.advance_key = self.assigned
        overdrive_ip = self.field_overdrive_ip.GetValue()
        overdrive_port = int(self.field_overdrive_port.GetValue())
        log_level = self.log_levels[self.choice_log_level.GetString(self.choice_log_level.GetSelection())]
        logging.getLogger().setLevel(log_level)
        self.parent.overdrive_connection = (overdrive_ip, overdrive_port)
        self.parent.superdrive_port = int(self.field_superdrive_port.GetValue())
        self.parent.super_keyword = self.field_super_keyword.GetValue()
        self.parent.press_delay = float(self.field_press_delay.GetValue())
        if self.parent.overdrive.listening:
            self.parent.overdrive.listening = False
        self.parent.overdrive = Listener(self.parent, self.parent.overdrive_connection, self.parent.super_keyword, self.parent.advance_key)
        self.parent.overdrive.start()
        self.Destroy()
        
class AboutFrame(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.parent = parent
        self.SetTitle(f'{self.parent.title} - About')
        self.SetIcon(wx.Icon('img/icon.ico'))
        self.panel_main = wx.Panel(self)
        self.sizer_main = wx.FlexGridSizer(6,1,10,10)
        self.font = wx.Font(12, wx.FONTFAMILY_MODERN, 0, 90, underline = False, faceName ="Arial Bold")
        self.logo = wx.Image('img/icon.png', wx.BITMAP_TYPE_PNG)
        self.bitmap_logo = wx.StaticBitmap(self.panel_main,bitmap=self.logo.ConvertToBitmap())
        self.label_program_name = wx.StaticText(self.panel_main, label=self.parent.title)
        self.label_program_name.SetFont(self.font)
        self.label_byline = wx.StaticText(self.panel_main, label="by Tom Smith for Nexstar Media Inc.")
        self.label_email = wx.StaticText(self.panel_main, label="thomas.smith@woodtv.com")
        self.label_phone_cell = wx.StaticText(self.panel_main, label="Cell: (231) 343.9803")
        self.label_phone_desk = wx.StaticText(self.panel_main, label="Desk: (616) 456.8888 Ext. 4319")
        
        self.sizer_main.AddMany([(self.bitmap_logo,1,wx.ALL|wx.CENTER|wx.ALIGN_CENTER),
                                 (self.label_program_name,1,wx.ALL|wx.CENTER|wx.ALIGN_CENTER),
                                 (self.label_byline,1,wx.ALL|wx.CENTER|wx.ALIGN_CENTER),
                                 (self.label_email,1,wx.ALL|wx.CENTER|wx.ALIGN_CENTER),
                                 (self.label_phone_cell,1,wx.ALL|wx.CENTER|wx.ALIGN_CENTER),
                                 (self.label_phone_desk,1,wx.ALL|wx.CENTER|wx.ALIGN_CENTER)])
        
        self.panel_main.SetSizerAndFit(self.sizer_main)
        self.SetInitialSize(self.GetBestSize())
        self.Layout()
        self.Show()
        
        
        
def main():
    logger = logging.getLogger(__name__)
    if os.path.isfile('settings.pkl'):
        with open('settings.pkl','rb') as file:
            overdrive_connection, superdrive_port, super_keyword, advance_key, press_delay, log_level = pickle.load(file)
            file.close()
    else:
        overdrive_connection = ('10.10.78.10', 8760)
        superdrive_port = 8888
        super_keyword = "XPN 1 MOS CG"
        advance_key = "space"
        press_delay = 0.5
        log_level =  logging.INFO
    app=[]; app = wx.App(None)
    frame = MainFrame(overdrive_connection, superdrive_port, super_keyword, advance_key, press_delay, logger, log_level)
    app.SetTopWindow(frame)
    app.MainLoop()
        
if __name__ == "__main__":
    main()