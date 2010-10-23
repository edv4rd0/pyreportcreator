"""This contains the classes for the main panel's presentation"""

import wx
import wx.lib.agw.flatnotebook as fnb
from pubsub import pub
import selectpanel
from pyreportcreator.profile import profile

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
        self.create_right_click_menu()
        self.view.SetRightClickMenu(self._rmenu)
        #page = selectpanel.SelectPanel(self.view)
        #self.view.AddPage(page, "test page", select=False, imageId=-1)
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
        document = self.profile.new_document(docType, connID)
        #create document
        self.documentsOpen[document.documentID] = selectpanel.QueryController(self.view, document)
                
        #let things like the Profile panel know and update themselves (view, not model related)
        pub.sendMessage('newdocument', name = document.name, docId = document.documentID, docType = docType)

    def open_document(self, docType, documentID):
        """Add an already existing document to the editor"""
        if docType == 'query':
            try:
                self.view.SetSelection(self.documentsOpen[documentID].page)
            except KeyError:
                self.documentsOpen[documentID] = selectpanel.QueryController(self.view, self.profile.documents[documentID])
    
    def closing_tab(self, evt):
        """Check if it's saved, if not allow the user to save or discard"""
        evt.Veto()
        docId = self.view.GetPage(self.view.GetSelection()).documentID
        #check saved state of document
        if self.profile.documents[docId].state == 'saved':
            del self.documentsOpen[docId]
            self.view.DeletePage(self.view.GetSelection())
        else:
            dlg = SaveDiscardDialog(wx.GetApp().GetTopWindow())
            dlg.ShowModal()
            if dlg.res == 'save':
                self.profile.save_doc(docId)
                print "saved"
                
        print "closing tab"
        
    def update_editor_toolbar(self, evt):
        """
        This will update the toolbar type for the editor (if required)
        and will also check thing such as whether the document is saved enable/disable the Save button.
        """
        print "Page changed"
