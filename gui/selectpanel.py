"""A prototype for the query panel"""
import sys
import wx
import wx.lib.inspection
from wx.lib.agw.customtreectrl import CustomTreeCtrl
from pyreportcreator.datahandler import datahandler, querybuilder
from pyreportcreator.profile import query, profile
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from pubsub import pub
import querypanel
import sqlalchemy


class JoinPanel( wx.Panel ):
    """The layout code for the JoinPanel for the join dialog"""
    def __init__( self, parent, leftTable, rightTable):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 640,400 ), style = wx.TAB_TRAVERSAL )
        self.textExplanations = ["Include all records from the " + leftTable + "table but only those from the "\
                                 + rightTable + "table which match.", "Include only those records which match in both tables.",\
                                 "Include all records from the " + rightTable + "table but only those from the " + leftTable\
                                 + "table which match."]
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
		
        gSizer1 = wx.GridSizer( 2, 2, 0, 0 )
    	
        self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Table: " + leftTable, wx.DefaultPosition, (300, -1), 0 )
        self.m_staticText1.Wrap( -1 )
        gSizer1.Add( self.m_staticText1, 0, wx.ALL, 5 )

        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"Table: " + rightTable, wx.DefaultPosition, (300, -1), 0 )
        self.m_staticText3.Wrap( -1 )
        gSizer1.Add( self.m_staticText3, 0, wx.ALL, 5 )
		
        m_choice1Choices = []
        self.choiceLeft = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 300,-1 ), m_choice1Choices, 0 )
        self.choiceLeft.SetSelection( 0 )
        gSizer1.Add( self.choiceLeft, 0, wx.ALL, 5 )

        m_choice3Choices = []
        self.choiceRight = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 300,-1 ), m_choice3Choices, 0 )
        self.choiceRight.SetSelection( 0 )
        gSizer1.Add( self.choiceRight, 0, wx.ALL, 5 )
        bSizer1.Add( gSizer1, 0, wx.EXPAND, 5 )

        bSizer3 = wx.BoxSizer( wx.VERTICAL )

        self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Set the join type...", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )
        bSizer3.Add( self.m_staticText4, 0, wx.ALL, 5 )

        self.sliderJoin = wx.Slider( self, wx.ID_ANY, 1, 0, 2, wx.DefaultPosition, wx.Size( 600,-1 ), wx.SL_HORIZONTAL )
        bSizer3.Add( self.sliderJoin, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

        sizerExplain = wx.BoxSizer( wx.HORIZONTAL )

        self.tcExplain = wx.TextCtrl( self, wx.ID_ANY, self.textExplain[1], wx.DefaultPosition, wx.Size( 600,200 ), style = wx.TR_MULTILINE | wx.TR_READONLY)
        sizerExplain.Add( self.tcExplain, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

        bSizer3.Add( sizerExplain, 1, wx.ALL|wx.EXPAND, 5 )

        self.btnCancel = wx.Button(self, -1, "Cancel", size = (-1, -1))
        self.btnOk = wx.Button(self, -1, "Ok", size = (-1, -1))
        self.btnOk.Enabled(False)
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        buttonSizer.Add(self.btnCancel, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        buttonSizer.Add(self.btnOK, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        bSizer3.Add(buttonSizer, 0, wx.ALIGN_RIGHT)

        bSizer1.Add( bSizer3, 1, wx.EXPAND, 5 )

        self.SetSizer( bSizer1 )
        self.Layout()

        def __del__( self ):
            pass


class JoinDialog(wx.Dialog):
    """This allows users to configure a join between two tables"""
    def __init__(self, parent, query, tableOne = False, tableTwo = False, amEditing = False):
        """Initialize elements and bind"""
        wx.Dialog.__init__(self, parent, -1, "Configure Join", size=(640,400))
        if tableOne:
            self.panel = JoinPanel(self, tableOne, tableTwo)
        self.slider = self.panel.sliderJoin
        #data - editing query.joins
        self.query = query
        #get the colums for each table
        try:
            self.columnsLeft = datahandler.DataHandler.get_columns(self.query.engineID, tableOne)
            self.columnsRight = datahandler.DataHandler.get_columns(self.query.engineID, tableTwo)
        except sqlalchemy.exc.OperationalError:
            self.wrote = False
            pub.sendMessage('disconnected', connID = self.query.engineID)
            self.Close()
        #load up the data into the view
        #setup selections and data types for compatibility checks
        self.leftSelections = ['Choose a column...']
        self.leftSelectionsTypes = [""]
        self.leftColumnNames = [""]
        self.rightSelectionsTypes = [""]
        self.rightSelections = ['Choose a compatible column...']
        for i in self.columnsLeft:
            self.leftSelections.append(i[0] + "\t" + i[1].__visit_name__)
            self.leftSelectionsTypes.append(i[1])
            self.leftColumnNames.append(i[1])
        self.panel.choiceRight.AppendItem(self.rightSelections[0])
        if amEditing:
            #Below: the join we work on in this dialog. If user confirms changes it gets passed as arguments to
            # self.query.add_join()
            if self.query.joins[-1]:
                self.workingJoin = {'leftTable': self.query.joins[2][0], 'joiningTable': self.query.joins[1][0], \
                                    'type': self.query.joins[0], 'tableValue': self.query.joins[2][1], \
                                    'joiningValue': self.query.joins[1][1], 'opr': self.query.joins[3], \
                                    'fakeRight': self.query.joins[-1]}
            else:
                self.workingJoin = {'leftTable': self.query.joins[1][0], 'joiningTable': self.query.joins[2][0], \
                                    'type': self.query.joins[0], 'tableValue': self.query.joins[1][1], \
                                    'joiningValue': self.query.joins[2][1], 'opr': self.query.joins[3], \
                                    'fakeRight': self.query.joins[-1]}
            #because of the whole weird left/right joins we need to instantiate the panel here when editing
            self.panel = JoinPanel(self, tableOne = self.workingJoin['leftTable'], tableTwo = self.workingJoin['joiningTable'])
            ind = self.leftColumnNames.index(self.workingJoin['tableValue'])
            self.choiceLeft.SetSelection(ind)
            #Now, build the right choice options and set selection
            for r in self.columnsRight:
                self.rightSelectionsTypes.append((r[0] + "\t" + r[1].__visit_name__, r[1], r[0]))
                if r[1] == self.leftSelectionTypes[ind][1]:
                    self.rightSelections.append((r[0] + "\t" + r[1].__visit_name__, r[0]))
                    self.panel.choiceRight.AppendItem(r[0] + "\t" + r[1].__visit_name__)
                    if r[0] == self.workingJoin['joiningValue']:
                        choiceInd = len(self.rightSelections) - 1
            self.panel.choiceRight.SetSelection(choiceInd)
                    
        else:
            #Below: the join we work on in this dialog. If user confirms changes it gets passed as arguments to
            # self.query.add_join()
            self.workingJoin = {'leftTable': tableOne, 'joiningTable': tableTwo, 'type': 'inner', \
                                'tableValue': "", 'joiningValue': "", 'opr': '==', 'fakeRight': False}
            for r in self.columnsRight:
                self.rightSelections.append((r[0] + "\t" + r[1].__visit_name__, r[0]))
                self.rightSelectionsTypes.append((r[0] + "\t" + r[1].__visit_name__, r[1], r[0]))
                self.panel.choiceRight.AppendItem(r[0] + "\t" + r[1].__visit_name__)
            self.panel.choiceLeft.AppendItems(self.leftSelections)
            self.panel.choiceRight.AppendItem(self.rightSelections[0])
            self.panel.choiceLeft.SetSelection(0)
            self.panel.choiceRight.SetSelection(0)

        #Bind events
        self.slider.Bind(wx.EVT_SCROLL, self.change_join_type)
        self.panel.choiceLeft.Bind(wx.EVT_CHOICE, self.left_choice)
        self.panel.choiceRight.Bind(wx.EVT_CHOICE, self.right_choice)
        self.panel.btnCancel.Bind(wx.EVT_BUTTON, self.cancel)
        self.panel.btnOk.Bind(wx.EVT_OK, self.confirm)

    def left_choice(self, evt):
        """Sets the left column and updates the available columns in the right choice"""
        choice = self.panel.choiceLeft.GetCurrentSelection()
        if choice == 0:
            self.workingJoin['tableValue'] = None
            self.workingJoin['joiningValue'] = None
            self.panel.choiceRight.Clear()
            self.rightSelections = ['Choose a compatible column...']
            self.panel.choiceRight.AppendItem(self.rightSelections[0])
            for i in self.rightSelectionsTypes:
                self.rightSelections.append((i[0], i[2]))
                self.panel.choiceRight.AppendItem(i[0])
            self.panel.rightChoice.SetSelection(0)
            self.panel.btnOk.Enabled(False)
        else:
            #set values
            self.workingJoin['tableValue'] = self.leftColumnNames[choice]
            self.workingJoin['joiningValue'] = None
            #load up compatible columns into right hand side
            choiceType = self.leftSelectionsTypes[choice]
            self.rightSelections = ['Choose a compatible column...']
            for k in self.rightSelectionsTypes:
                if k[1] == choiceType:
                    self.rightSelections.append((k[0], k[2]))
            self.panel.choiceRight.Clear()
            self.panel.choiceRight.AppendItem(self.rightSelections[0])
            for i in self.rightSelections[1:]:
                self.panel.choiceRight.Appenditem(i[0])
            self.panel.choiceRight.SetSelection(0)
            self.panel.btnOk.Enabled(False)

    def right_choice(self, evt):
        """Handles CHOICE event from the right hand one"""
        choice = self.panel.choiceRight.GetCurrentSelection()
        if choice == 0:
            self.workingJoin['joiningValue'] = None
            self.panel.btnOk.Enabled(False)
        else:
            self.workingJoin['joiningValue'] = self.rightSelections[choice][1]
            if self.panel.choiceLeft.GetCurrentSelection() == 0:
                self.panel.btnOk.Enabled(False)
            else:
                self.panel.btnOk.Enabled(True)

    def change_join_type(self, evt):
        """Activated when the user moves the slider. This changes the join type and updates the view."""
        value = self.slider.GetValue()
        if value == 0:
            self.workingJoin['type'] = 'left'
            self.workingJoin['fakeRight'] = False
            self.panel.tcExplain.SetValue(self.panel.textExplain[0])
        elif value == 1:
            self.workingJoin['type'] = 'inner'
            self.workingJoin['fakeRight'] = False
            self.panel.tcExplain.SetValue(self.panel.textExplain[1])
        else:
            self.workingJoin['type'] = 'inner'
            self.workingJoin['fakeRight'] = True
            self.panel.tcExplain.SetValue(self.panel.textExplain[2])

    def cancel(self, evt):
        """Just quit without saving"""
        self.wrote = False
        self.Close()

    def confirm(self, evt):
        """Write stuff to query and close"""
        self.query.add_join(leftTable = self.workingJoin['leftTable'], joiningTable = self.workingJoin['joiningTable'], \
                            type = self.workingJoin['type'], tableValue = self.workingJoin['tableValue'], \
                            joiningValue = self.workingJoin['joiningValue'], opr = self.workingJoin['opr'],\
                            fakeRight = self.workingJoin['fakeRight'])
        self.query.change_made()
        self.wrote = True
        self.Close()
    

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
        self.treeDataItems = CustomTreeCtrl(self, size = (-1, -1), style = wx.SUNKEN_BORDER | wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS)
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

        #compile list of current select items to check against
        self.itemsAlreadySelected = []
        for t in self.query.selectItems.keys():
            for c in self.query.selectItems[t]:
                self.itemsAlreadySelected.append((t, c[0]))
             
        #load data
        connID = self.query.engineID
        try:
            d = self.dlg.treeDataItems.AddRoot(str(connID))           
            tables = datahandler.DataHandler.get_tables(connID)
            for tableName in tables:
                j = self.dlg.treeDataItems.AppendItem(d, tableName)
                self.dlg.treeDataItems.SetItemPyData(j, "table")
            
                columns = datahandler.DataHandler.get_columns(connID, tableName)
                for colTuple in columns:
                    if (tableName, colTuple[0]) not in self.itemsAlreadySelected:
                        if colTuple[2]:
                            colDesc = colTuple[0] + "[PK]"
                        else:
                            colDesc = colTuple[0]
                    
                        f = self.dlg.treeDataItems.AppendItem(j, colDesc)
                        self.dlg.treeDataItems.SetItemPyData(f, (tableName, colTuple))

        except sqlalchemy.exc.OperationalError:
            pub.sendMessage('disconnected', connID = self.query.engineID)
            self.dlg.Destroy()
        except IndexError:
            print IndexError, "update_view"
            self.dlg.Close()
        
        #load select items
        try:
            for t in self.query.selectItems:
                columns = datahandler.DataHandler.get_columns(connID, t)
        except sqlalchemy.exc.OperationalError:
            pub.sendMessage('disconnected', connID = self.query.engineID)
            self.dlg.Destroy()

    def close(self, evt):
        """Close dialog without adding select items"""
        self.update = False
        self.dlg.Close()

    def remove_item(self, evt):
        """Remove the selected item"""
        index = self.dlg.lbSelect.GetSelection()
        if index == wx.NOT_FOUND:
            return
        colTuple = self.dlg.lbSelect.GetClientData(index)
        self.selected_index.remove(colTuple)

        if colTuple[1][2]:
            colDesc = colTuple[1][0] + "[PK]"
        else:
            colDesc = colTuple[1][0]
        r = self.dlg.treeDataItems.GetRootItem()
        tables = r.GetChildren()
        for t in tables:
            if t.GetText() == colTuple[0]:
                self.dlg.treeDataItems.AppendItem(t, colDesc, data = colTuple)
        self.dlg.lbSelect.Delete(index)
        
    def add_item(self, evt):
        """add selected item"""
        item = self.dlg.treeDataItems.GetSelection()
        data = self.dlg.treeDataItems.GetItemPyData(item)
        
        if data != "table":
            try:
                table = data[0]
                column = data[1]
                self.dlg.treeDataItems.Delete(item)
            except IndexError, TypeError:
                return
            if (table, column) in self.selected_index:
                return
            else:
                self.selected_index.append((table, column))
                self.dlg.lbSelect.Append(column[0] + " " + column[1].__visit_name__ + " - " + table, (table, column))
            

    def add_chosen(self, evt):
        """Close dialog and add selected items"""
        try:
            if len(self.selected_index) > 0:
                for i in self.selected_index: #add new select items to query
                    self.query.add_select_item(i[0], i[1][0])
                self.update = True
            else:
                self.update = False
            self.dlg.Close()
        except sqlalchemy.exc.OperationalError:
            pub.sendMessage('disconnected', connID = self.query.engineID)
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
        #load any existing items from a saved query
        if self.query.state == 'saved':
            self.load_elements()
        #Button events
        self.selectPanel.btnAddSelect.Bind(wx.EVT_BUTTON, self.add_select_item)
        self.selectPanel.btnRemoveItem.Bind(wx.EVT_BUTTON, self.remove_items)
        self.selectPanel.joinButton(wx.EVT_BUTTON, self.configure_join)
        #ListCtrl events
        self.selectPanel.selectList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.activate_remove_btn)
        self.selectPanel.selectList.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.deactivate_remove_btn)

    def configure_join(self, evt):
        pass
    
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

    def load_elements(self):
        """This method loads already existing query elements in a saved query"""
        #load select items
        items = []
        for t in self.query.selectItems:
            for c in self.query.selectItems[t]:
                items.append((t, c))
        self.update_select_view(items) # <-- add selectItems to view
        
        
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
        #join area
        self.joinSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.joinText = wx.StaticText(self, -1, label = "Configure join...", size = (-1,-1))
        self.joinButton = wx.Button(self, -1, "Join", size = (-1, -1))
        self.joinSizer.Add(self.joinText, 1, wx.EXPAND | wx.ALL, 5)
        self.joinSizer.Add(self.joinButton, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        self.topSizer.Add(self.joinSizer, 0, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer( self.topSizer )
	self.Layout()

    #----------------------------------------------------------------------

class QueryToolbook(wx.Toolbook):
    """
    Toolbook class
    """

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
