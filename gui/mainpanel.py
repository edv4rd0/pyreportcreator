"""This contains the classes for the main panel's presentation"""
import os
import wx
import wx.lib.agw.flatnotebook as fnb
from pubsub import pub
import selectpanel
from pyreportcreator.profile import profile

class DataSourceDialog(wx.Dialog):
    """This is the dialog box for users to add new columns to the select from clause"""
    def __init__(self, parent, profile):
        """Initialize stuff and do layout"""
        wx.Dialog.__init__(self, parent, -1, "Select Database", size=(650,400))
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((-1,10), 0)
        stDescription = wx.StaticText(self, -1, "Select which database you need to build a query on.")
        sizer.Add(stDescription, 0, wx.ALL, 5)
        self.lbSelect = wx.ListBox(self, -1, size = (-1, -1), style = wx.SUNKEN_BORDER)
        self.listData = []
        #select items buttons
        sizer.Add(self.lbSelect, 1, wx.EXPAND | wx.ALL, 5)
        stTitle = wx.StaticText(self, -1, "Click OK to confirm.")
        sizer.Add(stTitle, 0, wx.ALL, 5)
        #dialog buttons
        self.btnCancel = wx.Button(self, -1, "Cancel", size = (-1, -1))
        self.btnOK = wx.Button(self, -1, "Ok", size = (-1, -1))

        dialogSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        dialogSizer.Add(self.btnCancel, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        dialogSizer.Add(self.btnOK, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        sizer.Add(dialogSizer, 0, wx.ALIGN_RIGHT)
        
        self.SetSizer(sizer)

        self.btnOK.Bind(wx.EVT_BUTTON, self.use_selected)
        self.btnCancel.Bind(wx.EVT_BUTTON, self.close)

        #load data connections
        for i in profile.connections:
            name = profile.connections[i][2]
            address = profile.connections[i][1]
            dbType = profile.connections[i][0]
            s = self.lbSelect.Append(name + ", " + address + " [" + dbType + "]")
            self.listData.append(i) 
        
    def close(self, evt):
        self.Close()

    def use_selected(self, evt):
        """Grab selected and close"""
        
        selectedIndex = self.lbSelect.GetSelection()
        if selectedIndex == wx.NOT_FOUND:
            return
        self.data = self.listData[selectedIndex]
        print self.data
        self.Close()




class SaveDiscardDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Save Before Closing?", size=(250, 210))
        vbox = wx.BoxSizer(wx.VERTICAL)
        stline = wx.StaticText(self, 11, 'Your work is unsaved! Save, or quit without saving?')
        vbox.Add(stline, 1, wx.ALIGN_CENTER|wx.TOP, 45)
        self.btnSave = wx.Button(self, -1, "Save")
        self.btnDiscard = wx.Button(self, -1, "Discard")
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        sizer.Add(self.btnDiscard, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        sizer.Add(self.btnSave, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        vbox.Add(sizer, 0, wx.ALIGN_CENTER)
        self.SetSizer(vbox)
        self.btnSave.Bind(wx.EVT_BUTTON, self.on_yes)
        self.btnDiscard.Bind(wx.EVT_BUTTON, self.on_no)
        
    def on_yes(self, event):
        self.res = 'save'
        self.Close()

    def on_no(self, event):
        self.res = 'dis'
        self.Close()

class MainNotebook(fnb.FlatNotebook):
    """This is the main work area"""
    def __init__(self, parent):
        """Initialize"""
        fnb.FlatNotebook.__init__(self, parent, wx.ID_ANY, style = wx.EXPAND | fnb.FNB_FF2)

class DocumentEditorController(object):
    """
    This keeps track of opened documents and initialises the editors etc.
    It handles events from MainNotebook and events to open various documents
    for editing will call method in this class.
    """
    documentsOpen = dict()
    
    
    def __init__(self, view, profile):
        """Initialize and bind to events"""
        self.view = view #the MainNotebook
        self.profile = profile
        #set right click menu
        #NOT IMPLEMENTED self.create_right_click_menu()
        #NOT IMPLEMENTED self.view.SetRightClickMenu(self._rmenu)
        
        #bind to events
        self.view.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CHANGED, self.update_editor_toolbar)
        #self.view.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSED, self.closed_tab)
        self.view.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.closing_tab)

        #subscribe to pubsub
        pub.subscribe(self.new_document, 'new_query')
        pub.subscribe(self.open_document, 'open_document')

    def create_right_click_menu(self):
        """
        Based on method from flatnotebook demo
        NOT IMPLEMENTED
        """
        self._rmenu = wx.Menu()
        item = wx.MenuItem(self._rmenu, wx.ID_ANY,
                           "Close Tab")
        self.view.Bind(wx.EVT_MENU, self.closing_tab, item)
        self._rmenu.AppendItem(item)

    def new_document(self, docType, connID = None):
        """
        Add a new document and open it in the editor.
        Note: this is NOT used for already existing documents.
        """
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
                
        dlg = DataSourceDialog(wx.GetApp().GetTopWindow(), self.profile)
        dlg.ShowModal()
        try:
            connID = dlg.data
        except AttributeError:
            return #the user has clicked cancel
        document = self.profile.new_document(docType, connID)
        #create document
        self.documentsOpen[str(document.documentID)] = selectpanel.QueryController(self.view, document, self.profile)
        
        #let things like the Profile panel know and update themselves (view, not model related)
        pub.sendMessage('newdocument', name = document.name, docId = document.documentID, docType = docType)

    def open_document(self, docType, documentID):
        """Add an already existing document to the editor"""
        if docType == 'query':
            try:
                self.view.SetSelection(self.documentsOpen[documentID].page)
            except KeyError:
                self.documentsOpen[documentID] = selectpanel.QueryController(self.view, self.profile.open_doc(documentID), self.profile)

    def close_tab(self, evt):
        """For the tab menu"""
        pass
        #self.view.DeletePage(self.view.GetSelection())
    
    def closing_tab(self, evt):
        """Check if it's saved, if not allow the user to save or discard"""
        docId = self.view.GetPage(self.view.GetSelection()).documentID
        #check saved state of document
        if self.profile.documents[docId].state == 'saved':
            del delf.profile.documents[docId]
            del self.documentsOpen[docId]
        elif self.profile.documents[docId].state == 'new':
            del delf.profile.documents[docId]
            del self.documentsOpen[docId]
            pub.sendMessage('removequery', docId = docId)
        else:
            dlg = SaveDiscardDialog(wx.GetApp().GetTopWindow())
            dlg.ShowModal()
            if dlg.res == 'save':
                del self.profile.documents[docId]
                self.profile.save_doc(docId)
                del self.documentsOpen[docId]
                print "saved"
            elif dlg.res == 'dis':
                del self.profile.documents[docId]
                del self.documentsOpen[docId]
            dlg.Destroy()
        print "closing tab"
        
    def update_editor_toolbar(self, evt):
        """
        This will update the toolbar type for the editor (if required)
        and will also check thing such as whether the document is saved enable/disable the Save button.
        """
        print "Page changed"
