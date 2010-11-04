import wx
import wx.xrc as xrc
from wx.lib.wordwrap import wordwrap
import wizards
from pyreportcreator.gui import gui, mainpanel, sidepanelcontrol
from pyreportcreator.profile import profile
from pubsub import pub
import os

class SaveOrDiscard(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, title = "Really quit?", size=(300, 210))

        panel = wx.Panel(self, -1)
        vbox = wx.BoxSizer(wx.VERTICAL)

        text = wx.StaticText(panel, -1, label = "There are unsaved items,")
        text2 = wx.StaticText(panel, -1, label = "really quit?")

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.btnSave = wx.Button(self, -1, 'Save', size=(70, 30))
        self.btnDiscard = wx.Button(self, -1, 'Discard', size=(70, 30))
        self.btnCancel = wx.Button(self, -1, 'Cancel', size=(70, 30))
        hbox.Add(self.btnDiscard, 1, wx.LEFT, 5)
        hbox.Add((-1,-1), 1)
        
        hbox.Add(self.btnCancel, 1, wx.RIGHT, 5)
        hbox.Add(self.btnSave, 1, wx.RIGHT, 5)

        vbox.Add(panel)
        vbox.Add((-1,-1), 1)
        vbox.Add(hbox, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM | wx.EXPAND, 10)

        self.SetSizer(vbox)

        #bind events
        self.btnDiscard.Bind(wx.EVT_BUTTON, self.discard)
        self.btnCancel.Bind(wx.EVT_BUTTON, self.cancel)
        self.btnSave.Bind(wx.EVT_BUTTON, self.save)

    def discard(self, evt):
        """User decides to discard"""
        self.result = "discard"
        self.Close()

    def cancel(self, evt):
        """User decides to cancel"""
        self.result = "cancel"
        self.Close()

    def save(self, evt):
        """User decides to save and close"""
        self.result = "save"
        self.Close()

                          

class Application(wx.App):

    
    def OnInit(self):
        """Bind events to gui."""
        self.profile = profile.Profile()
        self.frame = gui.MainFrame(None)
        self.dataPanelControl = sidepanelcontrol.DataPanelControl(self.frame.sidePanel.dataPanel, self.profile)
        self.profilePanelControl = sidepanelcontrol.ProfilePanelControl(self.frame.sidePanel.treeProfileObjects, self.profile)
        #initialize the document editor controller
        self.documentEditorControl = mainpanel.DocumentEditorController(self.frame.mainNoteBook, self.profile)
        
        # initialize menus and toolbars
        self.menu = gui.MainMenu(self.frame)
        self.toolbar = gui.MainToolBar(self.frame)
        #menu events
        self.Bind(wx.EVT_MENU, self.OnClose, self.menu.menuFileQuit)
        ## bind file/profile events
        self.Bind(wx.EVT_MENU, self.profile_new, self.menu.menuFileNewProject)
        self.Bind(wx.EVT_MENU, self.profile_open, self.menu.menuFileOpen)
        self.Bind(wx.EVT_MENU, self.profile_save_as, self.menu.menuFileSaveAs)
        ##Profile menu
        self.Bind(wx.EVT_MENU, self.new_query, self.menu.menuProjectNewQuery)
        ##help menu
        self.Bind(wx.EVT_MENU, self.about_dialog, self.menu.menuHelpAbout)
        # bind toolbar events
        self.Bind(wx.EVT_TOOL, self.add_data_source, id = 1)
        self.Bind(wx.EVT_TOOL, self.view_sql, id = 4)
        #start app
        self.frame.Maximize()
        self.frame.Show()
        return True

    def view_sql(self, evt):
        """
        Just redirects the event with a pubsub message, the mainpanel will pick it
        up and detect the current document and then deal with the rest
        """
        pub.sendMessage('viewsql')

    def new_query(self, evt):
        pub.sendMessage('new_query', docType = 'query')
        
    def OnClose(self, evt):
        """Exits application"""
        if self.profile.connState == "altered" or len([d.document for d in self.documentEditorControl.documentsOpen.values()\
                                                  if d.document.state == "altered"]) > 0:
            dlg = SaveOrDiscard(wx.GetApp().GetTopWindow())
            dlg.ShowModal()
            if dlg.result == "save":
                self.save_all_docs()
                self.profile.save_connections()
            elif dlg.result == "cancel":
                dlg.Destroy()
                return
            dlg.Destroy()
        del self.documentEditorControl
        self.frame.Close()

    def profile_new(self, evt):
        """Ask user to save, close project. Start new project."""
        #open dialog --> clicks yes --> profile object destroyed, all views holding profile info destroyed and replaced with default. 
        pass

    def profile_open(self, evt):
        """Used open file dialog box to allow user to select a file, then load it into the profile class. """
        if self.profile.connState == "altered" or len([d.document for d in self.documentEditorControl.documentsOpen.values()\
                                                  if d.document.state == "altered"]) > 0:
            dlg = SaveOrDiscard(wx.GetApp().GetTopWindow())
            dlg.ShowModal()
            if dlg.result == "save":
                self.save_all_docs()
                self.profile.save_connections()
            elif dlg.result == "cancel":
                dlg.Destroy()
                return
            dlg.Destroy()

        dlg = wx.FileDialog(wx.GetApp().GetTopWindow(), "Open Project", os.getcwd(), "", "*.pro", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            dlg.Destroy()
            if path[-4:] != ".pro":
                self.profile._fileName = path + ".pro"
            else:
                self.profile._fileName = path
            print self.profile._fileName
            #close all documents and reset
            self.documentEditorControl.reset()
                
    def profile_save(self, evt):
        """Calls save method of the profile class and does some checking annd handles any errors"""
        if self.profile._fileName == '':
            dlg = wx.FileDialog(wx.GetApp().GetTopWindow(), "Name your project file", os.getcwd(), "", "*.pro", wx.SAVE)
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                dlg.Destroy()
                if path[-4:] != ".pro":
                    self.profile._fileName = path + ".pro"
                else:
                    self.profile._fileName = path
                print self.profile._fileName
            else:
                return
        self.save_all_docs()

    def save_all_docs(self):
        """Iterate through all open docs and save them all"""
        for d in self.documentEditorControl.documentsOpen:
            if self.documentEditorControl.documentsOpen[d].document.state == 'altered':
                self.profile.save_doc(self.documentEditorControl.documentsOpen[d].document)

    def profile_save_as(self, evt):
        """Opens save as dialog box then calls the Profile class' save method"""
        dlg = wx.FileDialog(wx.GetApp().GetTopWindow(), "Save as", os.getcwd(), "", "*.pro", wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            dlg.Destroy()
            if path[-4:] != ".pro":
                path = path + ".pro"
            documents = [d.document for d in self.documentEditorControl.documentsOpen.values() if d.document.state == "altered"]
            self.profile.copy_and_save(path, documents)
        else:
            return

    def add_data_source(self, evt):
        """Runs a select data source wizard and handles any errors raised when adding it
        to the current profile"""
        if self.profile._fileName == '':
            dlg = wx.FileDialog(wx.GetApp().GetTopWindow(), "Name your project file", os.getcwd(), "", "*.pro", wx.SAVE)
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                dlg.Destroy()
                if path[-4:] != ".pro":
                    self.profile._fileName = path + ".pro"
                else:
                    self.profile._fileName = path
                print self.profile._fileName
            else:
                return
        wizards.WizardNewDataSource(self.frame, self.profile)

    def about_dialog(self, evt):
        """Loads and displays an about dialog box"""
        info = wx.AboutDialogInfo()
        info.Name = "Database Query Creator"
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
