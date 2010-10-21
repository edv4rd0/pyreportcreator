import wx
import wx.xrc as xrc
from wx.lib.wordwrap import wordwrap
import wizards
import gui
import mainpanel
import sidepanelcontrol
from pyreportcreator.profile import profile

class Application(wx.App):

    
    def OnInit(self):
        """Bind events to gui."""
        self.profile = profile.Profile()
        self.frame = gui.MainFrame(None)
        self.dataPanelControl = sidepanelcontrol.DataPanelControl(self.frame.sidePanel.dataPanel, self.profile)
        #initialize the document editor controller
        self.documentEditorControl = mainpanel.DocumentEditorController(self.frame.mainNoteBook)

        
        # initialize menus and toolbars
        self.menu = gui.MainMenu(self.frame)
        self.toolbar = gui.MainToolBar(self.frame)

        #menu events
        self.Bind(wx.EVT_MENU, self.OnClose, self.menu.menuFileQuit)
        ## bind file/profile events
        self.Bind(wx.EVT_MENU, self.profile_new, self.menu.menuFileNewProject)
        self.Bind(wx.EVT_MENU, self.profile_open, self.menu.menuFileOpen)
        self.Bind(wx.EVT_MENU, self.profile_save_as, self.menu.menuFileSaveAs)
        ##help menu
        self.Bind(wx.EVT_MENU, self.about_dialog, self.menu.menuHelpAbout)
        # bind toolbar events
        self.Bind(wx.EVT_TOOL, self.add_data_source, id = 1)
        #start app
        self.frame.Maximize()
        self.frame.Show()
        return True

    def OnClose(self, evt):
        """Exits application"""
        self.frame.Close()

    def profile_new(self, evt):
        """Ask user to save, close project. Start new project."""
        #open dialog --> clicks yes --> profile object destroyed, all views holding profile info destroyed and replaced with default. 
        pass

    def profile_open(self, evt):
        """Used open file dialog box to allow user to select a file, then load it into the profile class. """
        pass

    def profile_save(self, evt):
        """Calls save method of the profile class and does some checking annd handles any errors"""
        import profile
        try:
            Profile.Save()
        except:
            wx.MessageBox('File save failed! Try again, or alternative try re-saving using Save As.', 'Save Error')
        #wx.MessageBox('File save failed! Try again, or alternative try re-saving using Save As.', 'Save Error')


    def profile_save_as(self, evt):
        """Opens save as dialog box then calls the Profile class' save method"""
        pass

    def add_data_source(self, evt):
        """Runs a select data source wizard and handles any errors raised when adding it
        to the current profile"""
        wizards.WizardNewDataSource(self.frame)

    def about_dialog(self, evt):
        """Loads and displays an about dialog box"""
        info = wx.AboutDialogInfo()
        info.Name = "Edward's Report Builder"
        info.Version = "0.0.1 Devel"
        info.Copyright = "(C) 2010 Edward Williams"
        info.Description = wordwrap("This is a GUI based application for"
                                    "easy query and report creation",
                                    350, wx.ClientDC(self.frame))
        info.WebSite = ("http://www.twitter.com/edv4rd0", "@edv4rd0 on Twitter")
        info.Developers = ["Edward Williams"]
        info.License = wordwrap("BSD License", 500,
                            wx.ClientDC(self.frame))
        # Show the wx.AboutBox
        wx.AboutBox(info)
 

