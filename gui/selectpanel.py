"""A prototype for the query panel"""

import wx
import wx.lib.inspection
from pyreportcreator.datahandler import datahandler, querybuilder
from pyreportcreator.profile import query

class DataItemsDialog(wx.Dialog):
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title, size=(650,400))
        sizer = wx.BoxSizer(wx.VERTICAL)
        stTitle = wx.StaticText(self, -1, "Add new data object")
        sizer.Add((-1,10), 0)
        sizer.Add(stTitle, 0, wx.ALL, 5)
        stDescription = wx.StaticText(self, -1, "Select data objects from the left which you want to include in your query.")
        sizer.Add(stDescription, 0, wx.ALL, 5)
        self.selectSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.treeDataItems = wx.TreeCtrl(self, size = (-1, -1), style = wx.SUNKEN_BORDER)
        self.lcSelect = wx.ListCtrl(self, size = (-1,-1), style = wx.SUNKEN_BORDER)
        self.selectSizer.Add(self.treeDataItems, 1, wx.EXPAND | wx.ALL, 5)
       

        #select items buttons
        self.sizerButtons = wx.BoxSizer(wx.VERTICAL)
        self.btnAddSelect = wx.Button(self, -1, ">", size = (30, -1))
        self.sizerButtons.Add(self.btnAddSelect, 1, wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER_VERTICAL, 5)
        self.btnRemoveItem = wx.Button(self, -1, "<", size = (30, -1))
        self.sizerButtons.Add(self.btnRemoveItem, 1, wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER_VERTICAL, 5)
        self.selectSizer.Add(self.sizerButtons, 0, wx.ALIGN_CENTER_VERTICAL)
        self.selectSizer.Add(self.lcSelect, 1, wx.EXPAND | wx.ALL, 5)
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

class SelectController(object):
    """
    This class handles the events and actions coming from the various widgets/editors for select items, from tables,
    joins, groups and filters. It is the main controller for the view.

    This class contains the control code for the above, the WhereController handles the condition code.
    """
    def __init__(self):
        """Initialize and bind to events"""
        self.frame = TestFrame(None, -1, '')
        self.selectPanel = self.frame.panel
        self.selectPanel.btnAddSelect.Bind(wx.EVT_BUTTON, self.add_select_item)

    def add_select_item(self, evt):
        """This opens a dialog to allow the user to add a select item"""
        if self.check_for_which_database() == False:
            dlg = DataItemsDialog(self.frame, -1, "Select Data Items")
            dlg.ShowModal()

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
        
	wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL| wx.SUNKEN_BORDER )
        #self.SetBackgroundColour('#C9C0BB')
        self.topSizer = wx.BoxSizer(wx.VERTICAL)
        #select items area
        self.lcSelect = wx.ListCtrl(self, size = (-1,200), style = wx.SUNKEN_BORDER)
       
        self.topSizer.Add(self.lcSelect, 1, wx.EXPAND | wx.ALL, 5)
        #select items buttons
        self.sizerButtons = wx.BoxSizer(wx.HORIZONTAL)
        self.btnRemoveItem = wx.Button(self, -1, "Remove Selected", size = (-1, -1))
        self.sizerButtons.Add(self.btnRemoveItem, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        
        self.btnAddSelect = wx.Button(self, -1, "Add Item...", size = (-1, -1))
        self.sizerButtons.Add(self.btnAddSelect, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        
        
        self.topSizer.Add(self.sizerButtons, 0, wx.ALIGN_RIGHT)
        
        self.SetAutoLayout(True)
        self.SetSizer( self.topSizer )
	self.Layout()

        
class TestFrame( wx.Frame ):
    """Test frame"""
    def __init__(self, parent, id, title):
        """Initialize"""
        wx.Frame.__init__(self, parent, id, title, size = (800, 600))
        self.panel = SelectPanel(self)

	#self.Maximize()
        self.Centre()
        


class Application(wx.App):
    """Just a test application"""

    def __init__(self):
        """initialize"""
        wx.App.__init__(self)

        #init objects
        self.controller = SelectController()
        self.controller.frame.Show()

app = Application()
wx.lib.inspection.InspectionTool().Show()

app.MainLoop()
