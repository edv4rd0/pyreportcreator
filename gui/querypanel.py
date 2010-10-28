"""Test code for a query editor"""
import wx
from wx.lib import intctrl
from pubsub import pub
#from wx.lib.combotreebox import ComboTreeBox
#from wx.lib.popupctl import PopButton
import wx.lib.masked as masked
import sqlalchemy
from sqlalchemy.dialects.mysql import \
        BIGINT, BINARY, BIT, BLOB, BOOLEAN, CHAR, DATE, \
        DATETIME, DECIMAL, DECIMAL, DOUBLE, ENUM, FLOAT, INTEGER, \
        LONGBLOB, LONGTEXT, MEDIUMBLOB, MEDIUMINT, MEDIUMTEXT, NCHAR, \
        NUMERIC, NVARCHAR, REAL, SET, SMALLINT, TEXT, TIME, TIMESTAMP, \
        TINYBLOB, TINYINT, TINYTEXT, VARBINARY, VARCHAR, YEAR
from sqlalchemy import types
from pyreportcreator.datahandler import datahandler
from pyreportcreator.profile import timestampconv

def get_generic_type(columnType):
    """Recieves the type and returns the correct details for the GUI"""
    if isinstance(columnType, types.SmallInteger):
        return ("small")
    if isinstance(columnType, types.Integer):
        return ("integer")
    if isinstance(columnType, types.Numeric):
        return ("number", columnType.__dict__["precision"], columnType.__dict__["scale"]) 
    if isinstance(columnType, types.String):
        return ("string", columnType.__dict__["length"])
    if isinstance(columnType, types.Date):
        return ("date")
    if isinstance(columnType, types.Time):
        return ("time")
    if isinstance(columnType, types.DateTime):
        return ("datetime")
    else:
        raise TypeError()

def get_mysql_types(columnType):
    """Retrieves the MYSQL type"""
    
    if isinstance(columnType, TINYINT):
        if columnType.unsigned:
            return ("int", 0, 255, False)
        else:
            return ("int", -128, 127, False)
    if isinstance(columnType, SMALLINT):
        if columnType.unsigned:
            return ("int", 0, 65535, False)
        else:
            return ("int", -32768, 32767, False)
    if isinstance(columnType, INTEGER):
        if columnType.unsigned:
            return ("int", 0, 4294967295, True)
        else:
            return ("int", -2147483648, 2147483647, True)
    if isinstance(columnType, BIGINT):
        if columnType.unsigned:
            return ("int", 0, 18446744073709551615, True)
        else:
            return ("int", -9223372036854775808, 9223372036854775807, True)
    if isinstance(columnType, MEDIUMINT):
        if columnType.unsigned:
            return ("int", 0, 16777215, True)
        else:
            return ("int", -8388608, 8388607, True)
    if isinstance(columnType, NUMERIC):
        return ("numeric", columnType.__dict__["precision"], columnType.__dict__["scale"], columnType.unsigned) 
    if isinstance(columnType, types.String):
        return ("string", columnType.__dict__["length"])
    if isinstance(columnType, DATE):
        return ("date")
    if isinstance(columnType, TIME):
        return ("time")
    if isinstance(columnType, DATETIME):
        return ("datetime")
    if isinstance(columnType, YEAR):
        return ("year")
    else:
        print columnType
        raise TypeError()

class BigIntCtrl(intctrl.IntCtrl):
    """
    An integer ctrl for editing the variable of the condition ctrl
    """
    def __init__(self, parent, width, update_state, dataField):
        wx.IntCtrl(self, parent, -1, min = -9223372036854775808, max = 9223372036854775807, size = (width, -1))
        self.dataField = dataField
        self.dataField = self.lastValue = 0
        self.update_state()

class IntegerCtrl(intctrl.IntCtrl):
    """
    An integer ctrl for editing the variable of the condition ctrl
    """
    def __init__(self, parent, width, update_state, dataField):
        wx.IntCtrl(self, parent, -1, min = -2147483648, max = 2147483647, size = (width, -1))
        self.dataField = dataField
        self.dataField = self.lastValue = 0
        self.update_state()

class SmallIntCtrl(intctrl.IntCtrl):
    """
    An integer ctrl for editing the variable of the condition ctrl
    """
    def __init__(self, parent, width, update_state, dataField):
        wx.IntCtrl(self, parent, -1, min = 0, max = 32767, size = (width, -1))
        self.dataField = dataField
        self.dataField = self.lastValue = 0
        self.update_state()

class CustomIntCtrl(intctrl.IntCtrl):
    """
    An integer ctrl for editing the variable of the condition ctrl
    @Param: update_state is a reference to the method of the profile.Query class being edited.
    It is run to change state to 'altered'.
    """
    def __init__(self, parent, width, update_state, dataField, minimum, maximum, longBool):
        intctrl.IntCtrl.__init__(self, parent, -1, min = minimum, max = maximum, limited = True, allow_none = False, allow_long = longBool, size = (width, -1))
        self.dataField = dataField
        self.update_state = update_state
        self.dataField = 0
        self.update_state()

    def assign_value(self, evt):
        self.dataField = self.GetValue()
        self.update_state()

class CustomMaskedCtrl(masked.TextCtrl):
    """
    Abstract base class for my own custom masked controls
    @Param: update_state is a reference to the method of the profile.Query class being edited.
    It is run to change state to 'altered'.
    @Param: mask, the appropriate maks for the control
    @Param: value, the default value for the control
    """
    def __init__(self, parent, width, mask, value, update_state, dataField):
        masked.TextCtrl.__init__(self, parent, -1, value, mask = mask, size = (width, -1))
        self.dataField = dataField
        self.update_state = update_state

    def assign_value(self, evt):
        raise NotImplementedError("Subclass must implement abstract method")

class DateCtrl(CustomMaskedCtrl):
    """This is basically the date ctrl"""
    def __init__(self, parent, width, update_state, dataField):
        """Initialize and setup"""
        CustomMaskedCtrl.__init__(self, parent, width, "#{4} ## ##", "2010 12 31", update_state, dataField)
        self.lastValue = "2010 12 31"
        self.dataField = self.lastValue
        self.update_state()

    def assign_value(self, evt):
        curValue = self.GetValue()
        value = timestampconv.date_conv(curValue)
        if value == False:
            self.SetValue(self.lastValue)
        else:
            self.lastValue = curValue
            self.dataField = value
            self.update_state()
        
class TimeCtrl(CustomMaskedCtrl):
    """This is basically the date ctrl"""
    def __init__(self, parent, width, update_state, dataField):
        """Initialize and setup"""
        CustomMaskedCtrl.__init__(self, parent, width, "##:## ##", "24:00 00", update_state, dataField)
        self.lastValue = "24:00 00"
        self.dataField = self.lastValue
        self.update_state()

    def assign_value(self, evt):
        curValue = self.GetValue()
        value = timestampconv.time_conv(curValue)
        if value == False:
            self.SetValue(self.lastValue)
        else:
            self.lastValue = curValue
            self.dataField = value

class DateTimeCtrl(CustomMaskedCtrl):
    """This is basically the date ctrl"""
    def __init__(self, parent, width, update_state, dataField):
        """Initialize and setup"""
        CustomMaskedCtrl.__init__(self, parent, width, "#{4} ## ## - ##:## ##", "2010 12 31 - 24:00 00", update_state, dataField)
        self.lastValue = "2010 12 31 - 24:00 00"
        self.dataField = self.lastValue
        self.update_state()
        
    def assign_value(self, evt):
        curValue = self.GetValue()
        value = timestampconv.datetime_conv(curValue)
        if value == False:
            self.SetValue(self.lastValue)
        else:
            self.lastValue = curValue
            self.dataField = value

class BetweenValue(wx.Panel):
    """This class allows a date, time or date time range control to be built"""
    def __init__(self, parent, dataField, ctrlType = 'numeric',  precision = None, decimalPlaces = None):
        wx.Panel.__init__(self, parent, -1)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        if ctrlType == 'numeric':
            self.ctrl1 = NumericCtrl(self, dataField[0], precision, decimalPlaces)
            self.ctrl2 = NumericCtrl(self, dataField[1], precision, decimalPlaces)
        elif ctrlType == 'integer':
            self.ctrl1 = IntegerCtrl(self, dataField[0])
            self.ctrl2 = IntegerCtrl(self, dataField[1])
        elif ctrlType == 'tiny_int':
            self.ctrl1 = TinyIntCtrl(self, dataField[0])
            self.ctrl2 = TinyIntCtrl(self, dataField[1])
        sizer.Add(self.ctrl1, 1)
        sizer.Add(self.ctrl2, 1)
        self.SetSizer(sizer)

class DateBetweenValue(wx.Panel):
    """This class allows a date, time or date time range control to be built"""
    def __init__(self, parent, dataField, ctrlType = 'float'):
        wx.Panel.__init__(self, parent, -1)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        if ctrlType == 'date':
            self.ctrl1 = DateCtrl(self, dataField[0])
            self.ctrl2 = DateCtrl(self, dataField[1])
        elif ctrlType == 'time':
            self.ctrl1 = TimeCtrl(self, dataField[0])
            self.ctrl2 = TimeCtrl(self, dataField[1])
        elif ctrlType == 'datetime':
            self.ctrl1 = DateTimeCtrl(self, dataField[0])
            self.ctrl2 = DateTimeCtrl(self, dataField[1])
        sizer.Add(self.ctrl1, 1)
        sizer.Add(self.ctrl2, 1)
        self.SetSizer(sizer)
        

class PickColumnDialog(wx.Dialog):
    """This class implements a column picker for choosing the column for a condition"""
    def __init__(self, parent, query):
        """Initialise and set up things"""
        wx.Dialog.__init__(self, parent, -1, size = (200,300))
        self.column = None #the variable for the new column
        self.query = query
        panel = wx.Panel(self, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.tree = wx.TreeCtrl(panel, style = wx.TR_HIDE_ROOT | wx.EXPAND| wx.SUNKEN_BORDER | wx.TR_HAS_BUTTONS)
        self.root = self.tree.AddRoot("root")
        self.button = wx.Button(panel, -1, "Close", size= (-1,-1), style = wx.EXPAND)
        sizer.Add(self.tree, 1, wx.EXPAND)
        sizer.Add(self.button, 0, wx.EXPAND)
        panel.SetSizer(sizer)
        panel.Layout()
        self.Center()
        self.load_items()
        #bind to events
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.select)
        self.button.Bind(wx.EVT_BUTTON, self.close)

    def close(self, evt):
        self.Close()

    def load_items(self):
        """Load items into column picker"""
        for t in self.query.selectItems:
            tableItem = self.tree.AppendItem(self.root, t)
            self.tree.SetPyData(tableItem, "table")
            columns = datahandler.DataHandler.get_columns(self.query.engineID, t)
            for c in columns:
                if isinstance(c[1], types._Binary) == False and isinstance(c[1], types.PickleType) == False:
                    citem = self.tree.AppendItem(tableItem, c[0])
                    self.tree.SetPyData(citem, (t, c[0], c[1]))
        
    def select(self, evt):
        item = self.tree.GetSelection()
        print item
        data = self.tree.GetItemData(item).GetData()
        if data != "table":
            self.change_text_confirm(data)
        else:
            self.change_text_close()

    def change_text_close(self):
        """Change text"""
        self.column = None
        self.button.SetLabel("Cancel")

    def change_text_confirm(self, data):
        """Change Text"""
        self.column = data
        self.button.SetLabel("Confirm")


class WhereController(object):
    """
    This class handles the gui events etc relating to the where clause
    """
    wherePanel = None
    elementControllers = dict()
    
    def __init__(self, view, query):
        """Initialize stuff so events can be monitored"""
        
        self.query = query
        self.whereEditor = view
        self.wherePanel = view.panel
        #bind to events
        self.whereEditor.btnAdd.Bind(wx.EVT_BUTTON, self.add_condition)
        self.whereEditor.btnSub.Bind(wx.EVT_BUTTON, self.add_set)
        #boolval for top set of query
        self.whereEditor.choiceLogic.Bind(wx.EVT_CHOICE, self.alter_boolval)

    def update_wherepanel(self):
        self.wherePanel.topSizer.Layout()
        self.wherePanel.layout_magic()

    def set_condition_column(self):
        """
        This runs the PickConditionColumn dialog and allows the user to select the column for their condition.
        """
        dlg = PickColumnDialog(wx.GetApp().GetTopWindow(), self.query)
        dlg.ShowModal()
        return dlg.column

    def change_made(self):
        """Called by condition/set controllers"""
        self.query.change_made()

    def alter_boolval(self, evt):
        """Change the joining bool of the top set of the query"""
        index = self.whereEditor.choiceLogic.GetCurrentSelection()
        self.query.conditions.boolVal = self.whereEditor.logicChoices[index]
        self.query.change_made() #change state to altered

    def add_condition(self, evt):
        """Add condition to top level"""

        #new condition    
        cond = self.query.add_condition(parent = self.query.conditions)
        #set view and controller
        view = ConditionEditor(self.wherePanel, cond.condID)
        self.elementControllers[cond.condID] = ConditionEditorControl(view, cond, whereController = self) 
        self.wherePanel.topSizer.Insert(0, view.topSizer, 0, wx.EXPAND | wx.ALL)
        self.wherePanel.topSizer.Layout()
        self.wherePanel.layout_magic()
        self.query.change_made() #change state to altered
        
    def add_set(self, evt):
        """Add condition set to top level"""
        cond = self.query.add_set(self.query.conditions)
        view = SetEditor(self.wherePanel, 6)
        self.elementControllers[cond.condID] = SetEditorControl(view, cond, whereController = self)
        self.wherePanel.topSizer.Insert(0, view, 0, wx.EXPAND | wx.ALL)
        self.wherePanel.topSizer.Layout()
        self.wherePanel.layout_magic()
        self.query.change_made() #change state to altered
        
    def add_child_set(self, object):
        """Not being implemented in this version"""
        pass

    def remove_condition(self, panel, condSizer, condObj):
        """Remove a condition editor from the containing sizer"""
        try:
            condSizer.DeleteWindows()
        except AttributeError: #if condSizer is an int (when deleting a set whith children)
            panel.topSizer.GetItem(condSizer).DeleteWindows()
        panel.topSizer.Remove(condSizer)
        panel.Layout()
        self.wherePanel.Layout()
        self.wherePanel.layout_magic()
        condObj.remove_self()
        del self.elementControllers[condObj.condID]
        self.query.change_made()

    def remove_set(self, parentPanel, panel, condSet):
        """
        Remove a query set from the where condition.
        This must check for any child conditions.
        If there are any it must:
          - Ask the user for confirmation
          - Delete each sub condition
          - delete the set
          - update the panel
        @Params:
        parentPanel: the panel of the parent condition set, or the top QueryPanel
        panel: the actual panel to be removed from the view
        """
        children = [j for j in panel.topSizer.GetChildren()]
        if len(children) > 1: #basically checking sizer length/num of sizer items (1 means just the set controls)
            dlg = wx.MessageBox("Really delete this set of conditions? This action will delete the child conditions!", "Confirm Delete", wx.OK | wx.CANCEL, wx.GetApp().GetTopWindow())
            if dlg == 4:
                for i in children[1:]:
                    index = panel.topSizer.GetChildren().index(i)
                panel.topSizer.DeleteWindows()
                panel.Destroy()
                condSet.remove_self()
                #remove controller objects
                self.remove_child_controllers(condSet.conditions)
                del self.elementControllers[condSet.condID]
                #update document state
                self.query.change_made()
                #layout parent panels
                parentPanel.Layout()
                self.wherePanel.layout_magic()
        else:
            panel.topSizer.DeleteWindows()
            panel.Destroy()
            parentPanel.Layout()
            condSet.remove_self()
            del self.elementControllers[condSet.condID]
            self.query.change_made()
            self.wherePanel.layout_magic()
        
    def add_sibling_condition(self, sizer, panel, ind, condObj):
        """Handles a message from pubsub"""
                #new condition    
        cond = self.query.add_condition(parent = condObj.parentObj, prev = condObj)
        #set view and controller
        szItem = panel.topSizer.GetItem(sizer)
        index = panel.topSizer.GetChildren().index(szItem)
            
        index += 1 #insert below element
        view = ConditionEditor(panel, cond.condID, ind)
        self.elementControllers[cond.condID] = ConditionEditorControl(view, cond, whereController = self) 
        panel.topSizer.Insert(index, view.topSizer, 0, wx.EXPAND | wx.ALL)
        panel.Layout()
        self.wherePanel.Layout()
        self.wherePanel.layout_magic()
        self.query.change_made() #change state to altered
        #get sizer and index


    def add_sibling_set(self, sizer, panel, ind, condObj):
        """
        Adds a sibling condition set
        """
        condSet = self.query.add_set(parent = condObj.parentObj, prev = condObj)
        szItem = panel.topSizer.GetItem(sizer)

        index = panel.topSizer.GetChildren().index(szItem)
            
        index += 1 #insert below element
        view = SetEditor(panel, condSet.condID)
        self.elementControllers[condSet.condID] = SetEditorControl(view, condSet, whereController = self)
        panel.topSizer.Insert( index, view, 0, wx.EXPAND | wx.ALL)
        panel.Layout()
        #self.wherePanel.Layout()
        self.wherePanel.layout_magic()
        self.query.change_made() #change state to altered

    def remove_child_controllers(self, children):
        """
        This takes a list of children and iterates through them removing all controllers for thos conditions.
        """
        for i in children:
            try: #first act as if it's a ConditionSet object
                self.remove_child_controllers(i.conditions)
                del self.elementControllers[i.condID]
            except AttributeError:
                #if it's a condition object
                del self.elementControllers[i.condID]
        
    def add_child_condition(self, parentSizer, ind, panel, parentSet):
        """
        This method adds a child condition to a sub condition set.
        @Param: parentSet is the parent ConditionSet object for the new Condition object.
        @Param: ind is the indentation appropriate for the condition editor widget set
        """
        cond = self.query.add_condition(parent = parentSet)
        #set view and controller
        view = ConditionEditor(panel, cond.condID, ind)
        self.elementControllers[cond.condID] = ConditionEditorControl(view, cond, whereController = self, top = False) 
        panel.topSizer.Insert(1, view.topSizer, 0, wx.EXPAND | wx.ALL)
        panel.Layout()
        self.wherePanel.topSizer.Layout()
        self.wherePanel.layout_magic()
        self.query.change_made() #change state to altered
            

class WhereEditor(wx.Panel):
    """
    This is the class containing everything else needed in the where clause of the query.
    """
    parent = None
    panel = None
    logicChoices = [ u"all", u"any" ]
    
    def __init__(self, parent):
        """Setup"""
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL| wx.SUNKEN_BORDER | wx.EXPAND)

        
        self.parent = parent
        self.panel = QueryPanel(self)
	self.topSizer = wx.BoxSizer( wx.VERTICAL )

	fgSizer3 = wx.FlexGridSizer( 1, 6, 0, 0 )
        fgSizer3.AddGrowableCol( 4,1 )
	fgSizer3.SetFlexibleDirection( wx.HORIZONTAL )
	fgSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
	
	self.stDesc1 = wx.StaticText( self, wx.ID_ANY, u"Match", wx.DefaultPosition, wx.DefaultSize, 0 )
	self.stDesc1.Wrap( -1 )
	fgSizer3.Add( self.stDesc1, 0, wx.ALL, 5 )
	
	self.choiceLogic = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.logicChoices, 0 )
	self.choiceLogic.SetSelection( 0 )
	fgSizer3.Add( self.choiceLogic, 0, wx.ALL, 5 )
	
	self.stDesc2 = wx.StaticText( self, wx.ID_ANY, u"of the following conditions:", wx.DefaultPosition, wx.DefaultSize, 0 )
	self.stDesc2.Wrap( -1 )
	fgSizer3.Add( self.stDesc2, 0, wx.ALL, 5 )

        fgSizer3.Add((0, 0), 1, wx.EXPAND)
	# Control Buttons
	self.btnAdd = wx.Button( self, wx.ID_ANY, u"+", wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
	fgSizer3.Add( self.btnAdd, 0, wx.ALL| wx.ALIGN_RIGHT, 5 )
        hBoxSpacing =  wx.BoxSizer( wx.HORIZONTAL)
	
	self.btnSub = wx.Button( self, wx.ID_ANY, u"...", wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
        hBoxSpacing.Add( self.btnSub, 0, wx.ALL | wx.ALIGN_RIGHT, 5 )
        hBoxSpacing.Add((2,-1), 0)
	fgSizer3.Add( hBoxSpacing, 0)
	self.topSizer.Add( fgSizer3, 0, wx.ALL | wx.EXPAND, 5 )
        self.topSizer.Add( self.panel, 1, wx.ALL | wx.EXPAND, 5)

        self.SetAutoLayout(True)
        self.SetSizer( self.topSizer )
	self.Layout()


    
class QueryCondEditor(object):
    """
    This is the abstract class for the editor for query conditions
    """
    parent = None
    indent = None

    def __init__(self, parent, condId, indentation = 0):
        """
        initialise the editor

        The 'indentation' param is for specifying how many spacers to put in.
        """
        self.parent = parent
        self.indentation = indentation


class SetEditor(QueryCondEditor, wx.Panel):
    """
    This class implements an editor for editing WHERE condition sets.
    Such as (condition1 OR condition2)
    """
    logicChoices = [ u"all", u"any" ]
    
    def __init__(self, parent, condId, indentation = 0):
        """Initialise the set"""
        QueryCondEditor.__init__(self, parent, indentation)
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL)
        
        self.condId = condId
        self.SetBackgroundColour('#C9C0BB')
	self.topSizer = wx.BoxSizer( wx.VERTICAL )
        #set indentation of element
        #if indentation == 0:
        #    fgSizer3 = wx.FlexGridSizer( 1, 7, 1, 1 )
        #    fgSizer3.AddGrowableCol( 4,0 )
        #else:
        #    fgSizer3 = wx.FlexGridSizer( 1, 8, 1, 1 )
        #    fgSizer3.AddGrowableCol( 5,0 )
        #    fgSizer3.Add((indentation, -1), 0)
        # Commented out: no arbitrary indentation in this version
        fgSizer3 = wx.FlexGridSizer( 1, 6, 1, 1 )
        fgSizer3.AddGrowableCol( 4,0 )

        #define rest of presentation
	fgSizer3.SetFlexibleDirection( wx.HORIZONTAL )
	fgSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
	
	self.stDesc1 = wx.StaticText( self, wx.ID_ANY, u"Match", wx.DefaultPosition, wx.DefaultSize, 0 )
	self.stDesc1.Wrap( -1 )
	fgSizer3.Add( self.stDesc1, 0, wx.ALL, 5 )
	
	self.choiceLogic = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.logicChoices, 0 )
	self.choiceLogic.SetSelection( 0 )
	fgSizer3.Add( self.choiceLogic, 0, wx.ALL, 5 )
	
	self.stDesc2 = wx.StaticText( self, wx.ID_ANY, u"of the following conditions:", wx.DefaultPosition, wx.DefaultSize, 0 )
	self.stDesc2.Wrap( -1 )
	fgSizer3.Add( self.stDesc2, 0, wx.ALL, 5 )

        fgSizer3.Add((0, 0), 1, wx.EXPAND)
	# Control Buttons
	self.btnDel = wx.Button( self, wx.ID_ANY, u"-", wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
	fgSizer3.Add( self.btnDel, 0, wx.ALL| wx.ALIGN_RIGHT, 5 )
	
	self.btnAdd = wx.Button( self, wx.ID_ANY, u"+", wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
	fgSizer3.Add( self.btnAdd, 0, wx.ALL| wx.ALIGN_RIGHT, 5 )

	#NOTE: Not going to support huge levels of sub sonditions in this version
	#self.btnSub = wx.Button( self, wx.ID_ANY, u"...", wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
        #fgSizer3.Add( self.btnSub, 0, wx.ALL| wx.ALIGN_RIGHT, 5 )
	
	self.topSizer.Add( fgSizer3, 0, wx.ALL | wx.EXPAND)

	
	self.SetSizer(self.topSizer)
        self.SetAutoLayout(True)
	self.Layout()

    def get_index_in_top_sizer(self):
        self.topSizer.GetItem(self, True)


class SetEditorControl(object):
    """This class implements a row of widgets for specifying a condition"""

    condition = None
    condType = None
    editor = None

    
    def __init__(self, conView, cond, whereController):
        """Setup editor control, bind to events"""
        
        #self.id = id #this will get replaced by the condition ID
        #self.condition = None
        self.editor = conView
        self.whereController = whereController
        self.cond = cond
        self.editor.btnAdd.Bind(wx.EVT_BUTTON, self.add_condition)
        self.editor.btnDel.Bind(wx.EVT_BUTTON, self.remove_set)

        #boolval for top set of query
        self.editor.choiceLogic.Bind(wx.EVT_CHOICE, self.alter_boolval)

    def alter_boolval(self, evt):
        """Change the joining bool of the top set of the query"""
        index = self.editor.choiceLogic.GetCurrentSelection()
        self.cond.boolVal = self.editor.logicChoices[index]
        self.whereController.change_made() #change state to altered
        
    def load_condition(self, condition):
        """
        This method accepts a condition object and loads it into the widget
        """
        self.condition = condition
        #Now load any elements into appropriate controls
        
        #Must check type of column/field1 to determine what widgets to load

    def add_condition(self, evt):
        """This handles the event and sends a message with the object"""
        ind = self.editor.indentation + 30
        parentSizer = self.editor.topSizer
        self.whereController.add_child_condition(parentSizer = parentSizer, ind = ind, panel = self.editor, parentSet = self.cond)

    def remove_set(self, evt):
        """
        Remove set and contained widgets
        """
        self.whereController.remove_set(parentPanel = self.editor.parent, panel = self.editor, condSet = self.cond)
    
class ConditionEditor(QueryCondEditor):
    """
    This is an editor or the presentation part of one to allow users to edit and configure a
    WHERE condition.

    Such as: column LIKE '%a'
    """
    
    operations = ['contains', 'equals', 'is in', 'not in', 'does not contain', 'not equal to']
    date_opr = ['between', 'equals', 'not equal to', 'not between', 'less than', 'greater than']
    
    def __init__(self, parent, condId, indentation = 0):
        """Initialise editor interface"""
        QueryCondEditor.__init__(self, parent, indentation)
        parent.ClearBackground()
        self.parent = parent
        #We are not going to have hugely deep nested conditions in this version
        if indentation == 0:
            self.topSizer = wx.FlexGridSizer( 1, 5, 1, 1 )
        else:
            self.topSizer = wx.FlexGridSizer(1, 4, 1, 1)
            
        self.condId = condId #for the purposes of clean removals
        self.topSizer.AddGrowableCol( 0 )
	self.topSizer.SetFlexibleDirection( wx.HORIZONTAL )
	self.topSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        hBoxSizer = wx.BoxSizer( wx.HORIZONTAL )

        if indentation > 0:
            hBoxSizer.AddSpacer(indentation, -1)
        
	#The column selector
        columnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.tcColumn = wx.TextCtrl(parent, wx.ID_ANY, "Select a column", wx.DefaultPosition, (-1,-1),  wx.TE_READONLY | wx.EXPAND)
        self.btnColumn = wx.Button(parent, wx.ID_ANY, "^", wx.DefaultPosition, (30, -1))
        columnSizer.Add(self.tcColumn, 1)
        columnSizer.Add(self.btnColumn, 0)
	hBoxSizer.Add( columnSizer, 1, wx.EXPAND | wx.ALL, 5 )
	
	self.choiceOperator = wx.Choice( parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.operations, 0 )
	self.choiceOperator.SetSelection( 0 )
	hBoxSizer.Add( self.choiceOperator, 1,wx.EXPAND | wx.ALL, 5 )
        #add box sizer with first three widgets to grid sizer
        self.topSizer.Add(hBoxSizer, 1, wx.EXPAND | wx.ALL)
	#The param widget(s)
	self.paramWidget = wx.TextCtrl( parent, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (450, -1), 0)
        self.paramSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.paramSizer.Add(self.paramWidget, 1)
        #self.paramWidget = wx.TextCtrl(parent, wx.ID_ANY, "", wx.DefaultPosition, (-1,-1),   wx.EXPAND)
	self.topSizer.Add( self.paramSizer, 1, wx.ALL, 5 )

        self.btnDel = wx.Button( parent, wx.ID_ANY, u" - ", wx.DefaultPosition, size = (40, -1))
	self.topSizer.Add( self.btnDel, 0, wx.ALL, 5 )
	self.btnAdd = wx.Button( parent, wx.ID_ANY, u" + ", wx.DefaultPosition, size = (40, -1))
	self.topSizer.Add( self.btnAdd, 1, wx.ALL, 5 )

        #We are not going to have hugely deep nested conditions in this version
        if indentation == 0:
            self.btnSub = wx.Button( parent, wx.ID_ANY, u"...", wx.DefaultPosition, size = (40, -1))
            self.topSizer.Add( self.btnSub, 1, wx.ALL, 5 )


class ConditionEditorControl(object):
    """This class implements a row of widgets for specifying a condition"""
    id = None
    condition = None
    condType = None
    editor = None
    
    def __init__(self, conView, condition, whereController, top = True):
        """Set up editor control, bind to events"""
        
        self.editor = conView
        self.condition = condition
        self.whereController = whereController
        self.editor.btnAdd.Bind(wx.EVT_BUTTON, self.add_condition)
        self.editor.btnDel.Bind(wx.EVT_BUTTON, self.remove)
        if top == True:
            self.editor.btnSub.Bind(wx.EVT_BUTTON, self.add_sub)
        self.editor.btnColumn.Bind(wx.EVT_BUTTON, self.set_column)
        self.typeDetails = ("string")


        
    def set_column(self, evt):
        """
        This method loads the set column dialog and changes the column to whatever the user decides
        """
        choice = self.whereController.set_condition_column()
        if choice != None: #If they click cancel/close this should not run
            self.condition.field1 = (choice[0], choice[1])
            self.editor.tcColumn.ChangeValue(choice[0]+"."+choice[1])
            print choice[2].__dict__
            self.typeDetails = get_mysql_types(choice[2])
            self.editor.choiceOperator.Clear()
            self.editor.paramSizer.Clear(True)
            print self.typeDetails
            if self.typeDetails[0] == "int":
                self.editor.choiceOperator.AppendItems(self.editor.date_opr)
                self.editor.choiceOperator.SetSelection( 0 )
                
                self.editor.paramWidget = CustomIntCtrl(parent = self.editor.parent, width = 450,\
                                                        update_state = self.whereController.change_made,\
                                                        dataField = self.condition.field2, minimum = self.typeDetails[1],\
                                                        maximum = self.typeDetails[2], longBool = self.typeDetails[3])
                
            else:
                self.editor.paramWidget = wx.TextCtrl( self.editor.parent, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (450, -1), 0)
            self.editor.paramSizer.Add(self.editor.paramWidget)
            #sizers and stuff need updating
            self.editor.topSizer.Layout()
            self.whereController.update_wherepanel()

    def set_field_widgets(self):
        pass
    
    def load_condition(self, condition):
        """
        This method accepts a condition object and loads it into the widget
        """
        self.condition = condition
        #Now load any elements into appropriate controls
        
        #Must check type of column/field1 to determine what widgets to load

    def add_condition(self, evt):
        """This handles the event and sends a message with the object"""
        
        sizer = self.editor.topSizer
        self.whereController.add_sibling_condition(sizer = sizer, panel = self.editor.parent, ind = self.editor.indentation, condObj = self.condition)

    def add_sub(self, evt):
        """
        This is called in the event of the editor.btnSub, or add child Set button being clicked
        """
        sizer = self.editor.topSizer
        self.whereController.add_sibling_set(sizer = sizer, panel = self.editor.parent, ind = self.editor.indentation, condObj = self.condition)


    def remove(self, evt):
        """Remove self"""
        sizer = self.editor.topSizer
        self.whereController.remove_condition(panel = self.editor.parent, condSizer = sizer, condObj = self.condition)

    def combo_operations(self, evt):
        """
        Handles the on click event on the operations combo box.
        The combo box changes the condition operation. The operation could be any standard SQL condition operator,
        such as '==', BETWEEN or NOT IN etc. Needless to say, this may change the parameter editor used.
        """
        if self.CBoperator.GetValue() == 'contains':
            pass

    def update_condition(self, evt):
        """
        This method is called in the event of the value of one of the condition widgets changing.
        It sends a pubsub request which is picked up by the query object and it then will alter the model
        """
        pass


class QueryPanel(wx.ScrolledWindow):
    """The panel for a query editor"""

    def __init__( self, parent ):
        """Initialize panel"""
        
	wx.ScrolledWindow.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL| wx.SUNKEN_BORDER | wx.VSCROLL)
        #wx.ScrolledWindow.__init__ ( self, parent, id = -1)
        self.SetBackgroundColour('#C9C0BB')
        self.SetScrollbars(1, 79, 150, 153)
	self.topSizer = wx.BoxSizer( wx.VERTICAL )
        self.SetAutoLayout(True)
        self.SetSizer( self.topSizer )
	self.Layout()
        self.SetVirtualSize(self.topSizer.CalcMin())

    def layout_magic(self):
        """This exists to set the virtual size of the scroll window to the size required by the sizer"""
        self.SetVirtualSize(self.topSizer.CalcMin())
