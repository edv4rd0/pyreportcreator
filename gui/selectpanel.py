"""A prototype for the query panel"""
import sys
import wx
import wx.lib.inspection
from pyreportcreator.datahandler import datahandler, querybuilder
from pyreportcreator.profile import query, profile
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

import querypanel


class DataItemsDialog(wx.Dialog):
    """This is the dialog box for users to add new columns to the select from clause"""
    def __init__(self, parent, id, title):
        """Initialize stuff and do layout"""
        wx.Dialog.__init__(self, parent, id, title, size=(650,400))
        sizer = wx.BoxSizer(wx.VERTICAL)
        stTitle = wx.StaticText(self, -1, "Add new data object")
        sizer.Add((-1,10), 0)
        sizer.Add(stTitle, 0, wx.ALL, 5)
        stDescription = wx.StaticText(self, -1, "Select data objects from the left which you want to include in your query.")
        sizer.Add(stDescription, 0, wx.ALL, 5)
        self.selectSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.treeDataItems = wx.TreeCtrl(self, size = (-1, -1), style = wx.SUNKEN_BORDER | wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS)
        self.lbSelect = wx.ListBox(self, -1, size = (-1, -1), style = wx.SUNKEN_BORDER)

        self.selectSizer.Add(self.treeDataItems, 1, wx.EXPAND | wx.ALL, 5)


        #select items buttons
        self.sizerButtons = wx.BoxSizer(wx.VERTICAL)
        self.btnAddSelect = wx.Button(self, -1, ">", size = (30, -1))
        self.sizerButtons.Add(self.btnAddSelect, 1, wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER_VERTICAL, 5)
        self.btnRemoveItem = wx.Button(self, -1, "<", size = (30, -1))
        self.sizerButtons.Add(self.btnRemoveItem, 1, wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER_VERTICAL, 5)
        self.selectSizer.Add(self.sizerButtons, 0, wx.ALIGN_CENTER_VERTICAL)
        self.selectSizer.Add(self.lbSelect, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.selectSizer, 1, wx.EXPAND)
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
#---------------------------------------------------------
class DataItemsDialogController(object):
    """This is the controller for the dialog to add data items"""
    def __init__(self, dlg, query):
        """Initialise and bind to controls"""
        
        self.query = query
        self.selected_index = [] #keep track of selected items
        #bind to controls
        self.dlg = dlg
        self.dlg.btnOK.Bind(wx.EVT_BUTTON, self.add_chosen)
        self.dlg.btnCancel.Bind(wx.EVT_BUTTON, self.close)
        self.dlg.btnAddSelect.Bind(wx.EVT_BUTTON, self.add_item)
        self.dlg.btnRemoveItem.Bind(wx.EVT_BUTTON, self.remove_item)
        

        #load data
        connID = self.query.engineID
        try:
            d = self.dlg.treeDataItems.AddRoot(str(connID))           
            tables = datahandler.DataHandler.get_tables(connID)
            for i in tables:
                j = self.dlg.treeDataItems.AppendItem(d, i)
                self.dlg.treeDataItems.SetPyData(j, (connID, i))
            
            (child, cookie) = self.dlg.treeDataItems.GetFirstChild(d)
            while child.IsOk(): 
                # do something with child
                c = self.dlg.treeDataItems.GetItemData(child).GetData()
                columns = datahandler.DataHandler.get_columns(c[0], c[1])
                for k in columns:
                    if k[2]:
                        colDesc = k[0] + "[PK]"
                    else:
                        colDesc = k[0]
                    
                    f = self.dlg.treeDataItems.AppendItem(child, colDesc)
                    self.dlg.treeDataItems.SetPyData(f, (c[0], c[1], k))
                (child, cookie) = self.dlg.treeDataItems.GetNextChild(d, cookie)
            
        except IndexError:
            print IndexError, "update_view"
            self.dlg.Close()

    def close(self, evt):
        """Close dialog without adding select items"""
        self.update = False
        self.dlg.Close()

    def remove_item(self, evt):
        """Remove the selected item"""
        index = self.dlg.lbSelect.GetSelection()
        if index == wx.NOT_FOUND:
            return
        self.dlg.lbSelect.Delete(index)
        del self.selected_index[index]
        
    def add_item(self, evt):
        """add selected item"""
        data = self.dlg.treeDataItems.GetItemData(self.dlg.treeDataItems.GetSelection()).GetData()
        try:
            table = data[1]
            column = data[2]
        except IndexError:
            return
        if (table, column) in self.selected_index:
            return
        else:
            self.selected_index.append((table, column))
            self.dlg.lbSelect.Append(column[0] + " " + column[1].__visit_name__ + " - " + table)
            

    def add_chosen(self, evt):
        """Close dialog and add selected items"""
        if len(self.selected_index) > 0:
            for i in self.selected_index:
                self.query.add_select_item(i[0], i[1][0])
            self.update = True
        else:
            self.update = False
        self.dlg.Close()

#---------------------------------------------------------


class SelectController(object):
    """
    This class handles the events and actions coming from the various widgets/editors for select items, from tables,
    joins, groups and filters. It is the main controller for the view.

    This class contains the control code for the above, the WhereController handles the condition code.
    """
    def __init__(self, view, query, profile):
        """Initialize and bind to events"""
        self.selectPanel = view
        self.query = query
        self.profile = profile
        self.selectItems = dict()
        #Button events
        self.selectPanel.btnAddSelect.Bind(wx.EVT_BUTTON, self.add_select_item)
        self.selectPanel.btnRemoveItem.Bind(wx.EVT_BUTTON, self.remove_items)
        #ListCtrl events
        self.selectPanel.selectList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.activate_remove_btn)
        self.selectPanel.selectList.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.deactivate_remove_btn)
        
    def add_select_item(self, evt):
        """This opens a dialog to allow the user to add a select item"""
        dlg = DataItemsDialog(wx.GetApp().GetTopWindow(), -1, "Select Data Items")
        control = DataItemsDialogController(dlg, self.query)
        dlg.ShowModal()
        if control.update:
            self.update_select_view(control.selected_index)
        dlg.Destroy()
            
    def update_select_view(self, items):
        """This updates the ListCtrl in the view"""
        self.selectPanel.selectList.Freeze()
        count = self.selectPanel.selectList.GetItemCount()
        for i in items:
            a = self.selectPanel.selectList.InsertStringItem(count, i[1][0])
        
            self.selectPanel.selectList.SetStringItem(count, 1, i[0])
            id = wx.NewId()
            self.selectPanel.selectList.SetItemData(a, id)
            self.selectItems[id] = i
        self.selectPanel.selectList.Thaw()
        
    def activate_remove_btn(self, evt):
        """Activate the remove selected item button"""
        self.selectPanel.btnRemoveItem.Enable(True)

    def deactivate_remove_btn(self, evt):
        """Deactivate the remove selected item button"""
        self.selectPanel.btnRemoveItem.Enable(False)

    def remove_items(self, evt):
        """This iterates through all selected items and removes them"""
        index = self.selectPanel.selectList.GetFirstSelected() 
        while index != -1:    
            try:
                id = self.selectPanel.selectList.GetItemData(index)
            
                try:
                    self.query.remove_select_item(table = self.selectItems[id][0], column = self.selectItems[id][1][0])
                    del self.selectItems[id]
                    #col1 = self.selectPanel.selectList.GetItem(index, 0)
                    #col2 = self.selectPanel.selectList.GetItem(index, 1)
                    self.selectPanel.selectList.DeleteItem(index)
                    #self.selectPanel.selectList.DeleteItem(col2)
                except profile.JoinException:
                    #TODO: yeah, need to beautify the message and add more info
                    dlg = wx.MessageDialog(parent=wx.GetApp().GetTopWindow(), message="There is a join between these two tables, are you sure you want to remove this?", caption="Check", style= wx.OK|wx.CANCEL|wx.ICON_QUESTION)
                    if dlg.ShowModal() == wx.ID_OK:
                        self.query.remove_select_item(table = self.selectItems[id][0], column = self.selectItems[id][1][0], force = True)
                        del self.selectItems[id]
                        col1 = self.selectPanel.selectList.GetItem(index, 0)
                        col2 = self.selectPanel.selectList.GetItem(index, 1)
                        self.selectPanel.selectList.DeleteItem(col2)
                        self.selectPanel.selectList.DeleteItem(col2)
                        dlg.Destroy()
                    else:
                        dlg.Destroy()
                        return
            except KeyError:
                print KeyError, "Item not removed"
                return
            index = self.selectPanel.selectList.GetNextSelected(index)

class SelectPanel(wx.Panel):
    """The panel for a query editor"""

    def __init__( self, parent ):
        """Initialize panel"""
        
	wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = (-1,-1), style = wx.TAB_TRAVERSAL| wx.SUNKEN_BORDER )
        self.topSizer = wx.BoxSizer(wx.VERTICAL)
        #select items area
        self.selectList = wx.ListCtrl(self, size = (-1,200), style = wx.SUNKEN_BORDER | wx.LC_REPORT)
        self.selectList.InsertColumn(0, "Column Name", width=-1)
        self.selectList.InsertColumn(1, "Table Name", width=-1)
        self.topSizer.Add(self.selectList, 1, wx.EXPAND | wx.ALL, 5)
        #select items buttons
        self.sizerButtons = wx.BoxSizer(wx.HORIZONTAL)
        self.btnRemoveItem = wx.Button(self, -1, "Remove Selected", size = (-1, -1))
        self.btnRemoveItem.Enable(False)
        self.sizerButtons.Add(self.btnRemoveItem, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        
        self.btnAddSelect = wx.Button(self, -1, "Add Item...", size = (-1, -1))
        self.sizerButtons.Add(self.btnAddSelect, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        
        
        self.topSizer.Add(self.sizerButtons, 0, wx.ALIGN_RIGHT)
        
        self.SetAutoLayout(True)
        self.SetSizer( self.topSizer )
	self.Layout()

class QueryToolbook(wx.Toolbook):
    """
    Toolbook class
    """
 
    #----------------------------------------------------------------------
    def __init__(self, parent, documentID):
        """Constructor"""
        wx.Toolbook.__init__(self, parent, wx.ID_ANY, style=
                             wx.BK_DEFAULT
                             #wx.BK_TOP
                             #wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
                            )
        self.documentID = documentID
        images = ("gui/icons/checkboxes32.png", "gui/icons/selectitems.png")
        # make an image list using the LBXX images
        il = wx.ImageList(32, 32)
        for i in images:
            il.Add(wx.Bitmap(i, wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)

        self.selectPage = SelectPanel(self)
        self.conditionEditor = querypanel.WhereEditor(self)
        
        self.AddPage(self.selectPage, "Select Items", 1, imageId = 1)
        self.AddPage(self.conditionEditor,"Add Conditions", imageId = 0)
 
        self.Bind(wx.EVT_TOOLBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_TOOLBOOK_PAGE_CHANGING, self.OnPageChanging)
 
    #----------------------------------------------------------------------
    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        print 'OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()
 
    #----------------------------------------------------------------------
    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        print 'OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()
        

class QueryController(object):
    """
    This controls top level events to do with displaying and editing the
    query definition.
    """
    def __init__(self, parent, document, profile):
        """Initialise, bind events, init other controllers and views"""
        #add tab to parent and make it selected
        self.parentView = parent
        self.document = document #need to keep tabs on the document we're editing
        self.toolbook = QueryToolbook(self.parentView, self.document.documentID)
        self.page = self.parentView.AddPage(self.toolbook, document.name, select = True)
        self.profile = profile

        #sub controllers
        self.selectController = SelectController(self.toolbook.selectPage, self.document, self.profile)
        self.conditionController = querypanel.WhereController(self.toolbook.conditionEditor, self.document)
