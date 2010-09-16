import wx
import wx.xrc as xrc
#imports form same package
import wizards

class Application(wx.App):
    
    def OnInit(self):
        """Loads xrc resource file for GUI and starts application."""
        self.res = xrc.XmlResource("resource.xrc")
 
        self.frame = self.res.LoadFrame(None, 'mainFrame')
        self.treeDataObjects = xrc.XRCCTRL(self.frame, 'treeDataObjects')
        self.treeDataSources = self.treeDataObjects.AddRoot('Data Sources')
        #menu events
        self.Bind(wx.EVT_MENU, self.OnClose, id=xrc.XRCID('fileExit'))
        ## bind file/profile events
        self.Bind(wx.EVT_MENU, self.profile_open, id=xrc.XRCID('fileOpen'))
        self.Bind(wx.EVT_MENU, self.profile_save, id=xrc.XRCID('fileSave'))
        self.Bind(wx.EVT_MENU, self.profile_save_as, id=xrc.XRCID('fileSaveAs'))
        # bind toolbar events
        self.Bind(wx.EVT_TOOL, self.add_data_source, id=xrc.XRCID('dataToolbar_addSource'))
        #start app
        self.frame.Maximize()
        self.frame.Show()
        return True

    def OnClose(self, evt):
        """Exits application"""
        self.frame.Close()

    def profile_open(self, evt):
        """Used open file dialog box to allow user to select a file, then load it into the profile class. """
        pass

    def profile_save(self, evt):
        """Calls save method of the profile class and does some checking and handles any errors"""
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
 
if __name__ == "__main__":
    app = Application(False)
    app.MainLoop()
