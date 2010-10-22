"""A prototype for the query panel"""
import sys
import wx
import wx.lib.inspection
from pyreportcreator.datahandler import datahandler, querybuilder
from pyreportcreator.profile import query
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
import querypanel


class AutoWidthListCtrl(wx.ListCtrl):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1,size = (-1,-1), style= wx. wx.SUNKEN_BORDER)
        #ListCtrlAutoWidthMixin.__init__(self)

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
        #dummy data
        r = self.treeDataItems.AddRoot("text")
        t = self.treeDataItems.AppendItem(r, "Table")
        self.treeDataItems.SetPyData(t, "table")
        self.treeDataItems.AppendItem(t, "column")
        #help(self.treeDataItems)
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
    def __init__(self, dlg, query = None):
        """Initialise and bind to controls"""
        self.dlg = dlg
        self.dlg.btnOK.Bind(wx.EVT_BUTTON, self.add_select_items)
        self.dlg.btnCancel.Bind(wx.EVT_BUTTON, self.close)
        self.dlg.btnAddSelect.Bind(wx.EVT_BUTTON, self.add)
    def close(self, evt):
        self.dlg.Destroy()
    def add_select_items(self, evt):
        self.dlg.Destroy()

    def add(self, evt):
        selectedItem = self.dlg.treeDataItems.GetSelection()
        if self.dlg.treeDataItems.GetPyData(selectedItem) == 'table':
            print "YO!"
#---------------------------------------------------------


class SelectController(object):
    """
    This class handles the events and actions coming from the various widgets/editors for select items, from tables,
    joins, groups and filters. It is the main controller for the view.

    This class contains the control code for the above, the WhereController handles the condition code.
    """
    def __init__(self, view):
        """Initialize and bind to events"""
        self.selectPanel = view
        #Button events
        self.selectPanel.btnAddSelect.Bind(wx.EVT_BUTTON, self.add_select_item)
        #ListCtrl events
        self.selectPanel.lbSelect.Bind(wx.EVT_LIST_ITEM_SELECTED, self.activate_remove_btn)
        self.selectPanel.lbSelect.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.deactivate_remove_btn)
        
    def add_select_item(self, evt):
        """This opens a dialog to allow the user to add a select item"""
        if self.check_for_which_database() == False:
            dlg = DataItemsDialog(wx.GetApp().GetTopWindow(), -1, "Select Data Items")
            control = DataItemsDialogController(dlg)
            dlg.ShowModal()

    def activate_remove_btn(self, evt):
        """Activate the remove selected item button"""
        self.selectPanel.btnRemoveItem.Enable(True)

    def deactivate_remove_btn(self, evt):
        """Deactivate the remove selected item button"""
        self.selectPanel.btnRemoveItem.Enable(False)

    def check_for_which_database(self):
        """
        This method is used to check if:
          - There are any column selected
          - if so, then which database they are from
        Returns: False, or the database
        """
        
        return False

        
class SelectPanel(wx.Panel):
    """The panel for a query editor"""

    def __init__( self, parent ):
        """Initialize panel"""
        
	wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = (-1,-1), style = wx.TAB_TRAVERSAL| wx.SUNKEN_BORDER )
        self.topSizer = wx.BoxSizer(wx.VERTICAL)
        #select items area
        self.lbSelect = wx.ListCtrl(self, size = (-1,200), style = wx.SUNKEN_BORDER)
       
        self.topSizer.Add(self.lbSelect, 1, wx.EXPAND | wx.ALL, 5)
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
    def __init__(self, parent):
        """Constructor"""
        wx.Toolbook.__init__(self, parent, wx.ID_ANY, style=
                             wx.BK_DEFAULT
                             #wx.BK_TOP
                             #wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
                            )
        images = ("gui/icons/checkboxes32.png", "gui/icons/selectitems.png")
        # make an image list using the LBXX images
        il = wx.ImageList(32, 32)
        for i in images:
            il.Add(wx.Bitmap(i, wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)

        self.selectPage = SelectPanel(self)
        self.conditionEditor = querypanel.WhereEditor(self)
        self.conditionPage = self.conditionEditor
        
        self.AddPage(self.selectPage, "Select Items", 1, imageId = 1)
        self.AddPage(self.conditionPage,"Add Conditions", imageId = 0)
 
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
    def __init__(self, parent, document):
        """Initialise, bind events, init other controllers and views"""
        #add tab to parent and make it selected
        self.parentView = parent
        self.toolbook = QueryToolbook(self.parentView)
        self.page = self.parentView.AddPage(self.toolbook, document.name, select = True)

        #sub controllers
        self.selectController = SelectController(self.toolbook.selectPage)
        self.conditionController = querypanel.WhereController(self.toolbook.conditionEditor)
