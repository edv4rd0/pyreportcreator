"""This contains the classes for the main panel's presentation"""
import os
import wx
import wx.lib.agw.flatnotebook as fnb
from pubsub import pub
import selectpanel
from pyreportcreator.profile import profile
from pyreportcreator.datahandler import querybuilder
import sqlalchemy

class ViewSQLDialog(wx.Dialog):
    """This dialog box displays the SQL for a query"""
    def __init__(self, parent, sqlaQuery):
        """Init view and display query"""
        wx.Dialog.__init__(self, parent, -1, "Display SQL", size=(450,300))
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.tcSQL = wx.TextCtrl(self, -1, sqlaQuery, size = (-1,80), style = wx.TE_READONLY | wx.TE_MULTILINE |\
                                 wx.BORDER_SUNKEN | wx.VSCROLL)
        self.btnOk = wx.Button(self, -1, "Close")
        sizer.Add(self.tcSQL, 1, wx.EXPAND| wx.BOTTOM, 5)
        sizer.Add(self.btnOk, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.SetSizer(sizer)

        self.btnOk.Bind(wx.EVT_BUTTON, self.close)

    def close(self, evt):
        """Close"""
        self.Close()

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
        wx.Dialog.__init__(self, parent, -1, "Save Before Closing?", size=(300, 150))
        vbox = wx.BoxSizer(wx.VERTICAL)
        stline = wx.StaticText(self, -1, 'Your work is unsaved!')
        stline2 = wx.StaticText(self, -1, 'Save, or quit without saving?')
        vbox.Add(stline, 0, wx.ALIGN_LEFT|wx.TOP | wx.LEFT, 5)
        vbox.Add(stline2, 1, wx.ALIGN_LEFT|wx.BOTTOM | wx.LEFT, 5)
        self.btnSave = wx.Button(self, -1, "Save")
        self.btnDiscard = wx.Button(self, -1, "Discard")
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        sizer.Add(self.btnDiscard, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        sizer.Add(self.btnSave, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        vbox.Add(sizer, 0,  wx.ALIGN_RIGHT)
        self.SetSizer(vbox)
        self.btnSave.Bind(wx.EVT_BUTTON, self.on_yes)
        self.btnDiscard.Bind(wx.EVT_BUTTON, self.on_no)
        self.res = 'dis'
        
    def on_yes(self, event):
        self.res = 'save'
        self.Close()

    def on_no(self, event):
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
        pub.subscribe(self.fail_close, 'failureclose')
        pub.subscribe(self.view_sql, 'viewsql')
        pub.subscribe(self.run_query, 'runquery')

    def close_all_tabs(self):
        """Close all tabs in notebook"""
        self.view.DeleteAllPages()

    def run_query(self):
        """
        Get current doc and run the query.
        This asks the user for a filename.
        """
        query = self.documentsOpen[self.view.GetCurrentPage().documentID].document
        try:
            builtQuery = querybuilder.build_query(query)
        except querybuilder.ClauseException:
            dlg = wx.MessageDialog(parent = wx.GetApp().GetTopWindow(),\
                                   message = "One or more of the query conditions are either empty or missing parameters, please check them and try again.",\
                                   caption = "Query Building Error", style = wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        except sqlalchemy.exc.OperationalError:
            dlg = wx.MessageDialog(parent = wx.GetApp().GetTopWindow(),\
                                   message = "There was an error connecting to the database. Please make sure it's up and try again.", \
                                   caption = "Database Connectivity Error", style = wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        #now run the built query
        try:
            dlg = wx.FileDialog(wx.GetApp().GetTopWindow(), "Choose Output File", os.getcwd(), "", "*.csv", wx.SAVE)
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                dlg.Destroy()
                if path[-4:] != ".csv":
                    path = path + ".csv"
                #write report to csv file
                querybuilder.run_report(builtQuery, query.engineID, path)
        except querybuilder.ClauseException:
            dlg = wx.MessageDialog(parent = wx.GetApp().GetTopWindow(),\
                                   message = "One or more of the query conditions are either empty or missing parameters, please check them and try again.",\
                                   caption = "Query Building Error", style = wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
        except sqlalchemy.exc.OperationalError:
            dlg = wx.MessageDialog(parent = wx.GetApp().GetTopWindow(),\
                                   message = "There was an error connecting to the database. Please make sure it's up and try again.", \
                                   caption = "Database Connectivity Error", style = wx.OK)
            dlg.ShowModal()
            dlg.Destroy()


    def view_sql(self):
        """Get current doc and then generate sql"""
        query = self.documentsOpen[self.view.GetCurrentPage().documentID].document
        try:
            builtQuery = querybuilder.build_query(query)
            dlg = ViewSQLDialog(wx.GetApp().GetTopWindow(), builtQuery.__str__())
            dlg.ShowModal()
            dlg.Destroy()
        except querybuilder.ClauseException:
            dlg = wx.MessageDialog(parent = wx.GetApp().GetTopWindow(),\
                                   message = "One or more of the query conditions are either empty or missing parameters, please check them and try again.",\
                                   caption = "Query Building Error", style = wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
        except sqlalchemy.exc.OperationalError:
            dlg = wx.MessageDialog(parent = wx.GetApp().GetTopWindow(),\
                                   message = "There was an error connecting to the database. Please make sure it's up and try again.", \
                                   caption = "Database Connectivity Error", style = wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            

    def fail_close(self, documentID):
        """This runs in the event of a database related error when opening a query"""
        del self.documentsOpen[documentID]

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

    def new_document(self, docType):
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
        self.documentsOpen[document.documentID] = selectpanel.QueryController(self.view, document, self.profile)
        
        #let things like the Profile panel know and update themselves (view, not model related)
        pub.sendMessage('newdocument', name = document.name, docId = document.documentID, docType = docType)

    def open_document(self, docType, documentID):
        """Add an already existing document to the editor"""
        if docType == 'query':
            try:
                self.view.SetSelection(self.documentsOpen[documentID].page)
            except KeyError:
                document = self.profile.load_doc(documentID)
                print document.documentID, documentID
                self.documentsOpen[document.documentID] = selectpanel.QueryController(self.view, document, self.profile)

    def close_tab(self, evt):
        """For the tab menu"""
        pass
        #self.view.DeletePage(self.view.GetSelection())
    
    def closing_tab(self, evt):
        """Check if it's saved, if not allow the user to save or discard"""
        docId = self.view.GetPage(self.view.GetSelection()).documentID
        print self.documentsOpen
        #check saved state of document
        if self.documentsOpen[docId].document.state == 'saved':
            del self.documentsOpen[docId]
        elif self.documentsOpen[docId].document.state == 'new':
            del self.profile.document_index[docId]
            del self.documentsOpen[docId]
            pub.sendMessage('removequery', docId = docId)
        else:
            dlg = SaveDiscardDialog(wx.GetApp().GetTopWindow())
            dlg.ShowModal()
            if dlg.res == 'save':
                #choose name
                namedlg = wx.TextEntryDialog(parent = wx.GetApp().GetTopWindow(), message = "Please a name for the query",
                                             caption = "Name query", defaultValue = self.documentsOpen[docId].document.name)
                if namedlg.ShowModal() == wx.ID_OK:
                    name = namedlg.GetValue()
                    self.documentsOpen[docId].document.name = name
                    namedlg.Destroy()
                #save document
                self.profile.save_doc(self.documentsOpen[docId].document)
                pub.sendMessage('namechanged', docId = docId, name = name)
                del self.documentsOpen[docId]
            elif dlg.res == 'dis':
                del self.documentsOpen[docId]
                pub.sendMessage('removequery', docId = docId)
            dlg.Destroy()
        
    def update_editor_toolbar(self, evt):
        """
        This will update the toolbar type for the editor (if required)
        and will also check thing such as whether the document is saved enable/disable the Save button.
        """
        print "Page changed"
