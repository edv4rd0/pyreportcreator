"""This contains the classes for the main panel's presentation"""

import wx
import wx.lib.agw.flatnotebook as fnb
from pubsub import pub
import selectpanel
from pyreportcreator.profile import profile


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
        #page = selectpanel.SelectPanel(self.view)
        #self.view.AddPage(page, "test page", select=False, imageId=-1)
        #bind to events
        self.view.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CHANGED, self.update_editor_toolbar)
        self.view.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSED, self.closed_tab)
        self.view.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.closing_tab)

        #subscribe to pubsub
        pub.subscribe(self.new_document, 'new_query')

    def new_document(self, docType, connID = None):
        """
        Add a new document and open it in the editor.
        Note: this is NOT used for already existing documents.
        """
        document = self.profile.new_document(docType, connID)
        if docType == 'query':
            try:
                self.view.SetSelection(self.documentsOpen[document.documentID].page)
            except KeyError:
                self.documentsOpen[document.documentID] = selectpanel.QueryController(self.view, document)
                #let things like the Profile panel know and update themselves
                pub.sendMessage('newdocument', name = document.name, docId = document.documentID, docType = docType)

    def add_document(self, documentID, controller):
        """Add an already existing document to the editor"""
        pass
    
    def closing_tab(self, evt):
        """Check if it's saved, if not allow the user to save or discard"""
        help(evt)
        print "closing tab"
        
    def closed_tab(self, evt):
        """Destroy the controller, view etc for the opened document"""
        
        print "closed tab"
        
    def update_editor_toolbar(self, evt):
        """
        This will update the toolbar type for the editor (if required)
        and will also check thing such as whether the document is saved enable/disable the Save button.
        """
        print "Page changed"
