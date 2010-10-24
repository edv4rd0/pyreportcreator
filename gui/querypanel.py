"""Test code for a query editor"""
import wx
from pubsub import pub
import wx.lib.inspection
from wx.lib.combotreebox import ComboTreeBox
from wx.lib.popupctl import PopButton
import wx.lib.masked as masked


class DateCtrl(masked.TextCtrl):
    """This is basically the date ctrl"""
    def __init__(self, parent):
        """Initialize and setup"""
        masked.TextCtrl.__init__(self, parent, -1, "2010 12 31", mask ="#{4} ## ##")
        
class TimeCtrl(masked.TextCtrl):
    """This is basically the date ctrl"""
    def __init__(self, parent):
        """Initialize and setup"""
        masked.TextCtrl.__init__(self, parent, -1, "24:00 00", mask ="##:## ##")

class DateTimeCtrl(masked.TextCtrl):
    """This is basically the date ctrl"""
    def __init__(self, parent):
        """Initialize and setup"""
        masked.TextCtrl.__init__(self, parent, -1, "2010 12 31 - 24:00 00", mask ="#{4} ## ## - ##:## ##")

class DateRange(wx.Panel):
    """This class allows a date, time or date time range control to be built"""
    def __init__(self, parent, ctrlType = 'date'):
        wx.Panel.__init__(self, parent, -1)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        if ctrlType == 'date':
            self.ctrl1 = DateCtrl(self)
            self.ctrl2 = DateCtrl(self)
        sizer.Add(self.ctrl1, 1)
        sizer.Add(self.ctrl2, 1)
        

class PopupFrame(wx.Frame):

    def __init__(self, parent, style=wx.DEFAULT_FRAME_STYLE & wx.FRAME_FLOAT_ON_PARENT):
        wx.Frame.__init__(parent, style = style)


class WhereController(object):
    """
    This class handles the gui events etc relating to the where clause
    """
    wherePanel = None
    elementControllers = []
    
    def __init__(self, view):
        """Initialize stuff so events can be monitored"""
        
        
        self.whereEditor = view
        self.wherePanel = view.panel
        #bind to events
        self.whereEditor.btnAdd.Bind(wx.EVT_BUTTON, self.add_condition)
        self.whereEditor.btnSub.Bind(wx.EVT_BUTTON, self.add_set)

        #pubsub subscriptions
        pub.subscribe(self.add_sibling_condition, 'where.insert.condition')
        pub.subscribe(self.remove_condition, 'where.remove.condition')
        pub.subscribe(self.add_child_condition, 'where.set_insert.condition')
        pub.subscribe(self.remove_set, 'where.remove.set')
        pub.subscribe(self.add_sibling_set, 'where.insert.sub_set')
        
    def add_condition(self, evt):
        """Add condition to top level"""
        c = ConditionEditor(self.wherePanel, 6)
        
        self.wherePanel.topSizer.Insert(0, c.topSizer, 0, wx.EXPAND | wx.ALL)
        self.wherePanel.Layout()
        self.wherePanel.layout_magic()
        
    def add_set(self, evt):
        """Add condition set to top level"""

        s = SetEditor(self.wherePanel, 6)
        self.wherePanel.topSizer.Insert(0, s, 0, wx.EXPAND | wx.ALL)
        self.wherePanel.Layout()
        self.wherePanel.layout_magic()
        
    def add_child_set(self, object):
        """Not being implemented in this version"""
        pass

    def remove_condition(self, queryID, panel, condSizer):
        """Remove a condition editor from the containing sizer"""
        if queryID == 0:
            try:
                condSizer.DeleteWindows()
            except AttributeError: #if condSizer is an int (when deleting a set whith children)
                panel.topSizer.GetItem(condSizer).DeleteWindows()

            panel.topSizer.Remove(condSizer)
            panel.Layout()
            self.wherePanel.Layout()
            self.wherePanel.layout_magic()

    def remove_set(self, queryID, parentPanel, panel):
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
        if queryID == 0:
            
            children = [j for j in panel.topSizer.GetChildren()]
            if len(children) > 1:
                dlg = wx.MessageBox("Really delete this set of conditions? This action will delete the child conditions!", "Confirm Delete", wx.OK | wx.CANCEL, wx.GetApp().GetTopWindow())
                if dlg == 4:
                    for i in children[1:]:
                        index = panel.topSizer.GetChildren().index(i)
                        self.remove_condition(queryID, panel, index)

                    panel.topSizer.DeleteWindows()
                    panel.Destroy()
                    parentPanel.Layout()
            else:
                panel.topSizer.DeleteWindows()
                panel.Destroy()
                parentPanel.Layout()
            self.wherePanel.layout_magic()

            
        
    def add_sibling_condition(self, queryID, sizer, panel, ind):
        """Handles a message from pubsub"""
        if queryID == 0:
            #get sizer and index
            
            szItem = panel.topSizer.GetItem(sizer)

            index = panel.topSizer.GetChildren().index(szItem)
            
            index += 1 #insert below element
        
            #setup Editor
            c = ConditionEditor(panel, 6, ind)
            panel.topSizer.Insert( index, c.topSizer, 0, wx.EXPAND | wx.ALL)
            panel.Layout()
            self.wherePanel.Layout()
            self.wherePanel.layout_magic()


    def add_sibling_set(self, queryID, sizer, panel, ind):
        """
        Adds a sibling condition set
        """
        if queryID == 0:
            szItem = panel.topSizer.GetItem(sizer)

            index = panel.topSizer.GetChildren().index(szItem)
            
            index += 1 #insert below element
        
            #setup Editor
            s = SetEditor(panel, 6, ind)
            panel.topSizer.Insert( index, s, 0, wx.EXPAND | wx.ALL)
            panel.Layout()
            self.wherePanel.Layout()
            self.wherePanel.layout_magic()
            

    def add_child_condition(self, queryID, parentSizer, ind, panel):
        """This method adds a child condition to a sub condition set"""
        if queryID == 0:
            #setup Editor
            c = ConditionEditor(panel, 6, ind)
            
            parentSizer.Insert(1, c.topSizer, 1, wx.EXPAND | wx.ALL)
            panel.Layout()
            self.wherePanel.Layout()
            self.wherePanel.layout_magic()
            

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
    id = None
    indent = None

    def __init__(self, parent, id, indentation = 0):
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
    elemID = 0
    
    def __init__(self, parent, id, indentation = 0):
        """Initialise the set"""
        QueryCondEditor.__init__(self, parent, id, indentation)
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL)
        
        
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

        #initialise controller - yeah, weird but good way to handle the killing of the controller
        self.controller = SetEditorControl(self)

    def get_index_in_top_sizer(self):
        self.topSizer.GetItem(self, True)


class ConditionEditor(QueryCondEditor):
    """
    This is an editor or the presentation part of one to allow users to edit and configure a
    WHERE condition.

    Such as: column LIKE '%a'
    """
    
    operations = ['contains', 'equals', 'is in', 'not in', 'does not contain', 'not equal to']
    date__opr = ['between', 'equals', 'not equal to', 'not between']
    
    def __init__(self, parent, id, indentation = 0):
        """Initialise editor interface"""
        QueryCondEditor.__init__(self, parent, id, indentation)
        parent.ClearBackground()
        #We are not going to have hugely deep nested conditions in this version
        if indentation == 0:
            self.topSizer = wx.FlexGridSizer( 1, 5, 1, 1 )
        else:
            self.topSizer = wx.FlexGridSizer(1, 4, 1, 1)
            
        self.topSizer.AddGrowableCol( 1 )
	self.topSizer.SetFlexibleDirection( wx.HORIZONTAL )
	self.topSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        hBoxSizer = wx.BoxSizer( wx.HORIZONTAL )

        if indentation > 0:
            hBoxSizer.AddSpacer(indentation, -1)
        
	#self.columnSelector = wx.combo.ComboCtrl(parent, style = wx.CB_READONLY)
	self.columnSelector = ComboTreeBox(parent, style = wx.CB_READONLY|wx.CB_SORT)
        #quick tets populate:
        item1 = self.columnSelector.Append('Item 1')
        item1a = self.columnSelector.Append('Item 1a', parent=item1)
	hBoxSizer.Add( self.columnSelector, 1,wx.ALL, 5 )
	
	self.choiceOperator = wx.Choice( parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.operations, 0 )
	self.choiceOperator.SetSelection( 0 )
	hBoxSizer.Add( self.choiceOperator, 1,wx.ALL, 5 )
        #add box sizer with first three widgets to grid sizer
        self.topSizer.Add(hBoxSizer, 1, wx.ALL)
	#The param widget(s)
	#self.paramWidget = wx.TextCtrl( parent, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (350, -1), 0)
        self.paramWidget = DateCtrl(parent)
	self.topSizer.Add( self.paramWidget, 1, wx.EXPAND| wx.ALL, 5 )

        self.btnDel = wx.Button( parent, wx.ID_ANY, u" - ", wx.DefaultPosition, size = (40, -1))
	self.topSizer.Add( self.btnDel, 1, wx.ALL, 5 )
	self.btnAdd = wx.Button( parent, wx.ID_ANY, u" + ", wx.DefaultPosition, size = (40, -1))
	self.topSizer.Add( self.btnAdd, 1, wx.ALL, 5 )

        #We are not going to have hugely deep nested conditions in this version
        if indentation == 0:
            self.btnSub = wx.Button( parent, wx.ID_ANY, u"...", wx.DefaultPosition, size = (40, -1))
            self.topSizer.Add( self.btnSub, 1, wx.ALL, 5 )
        #set controller
            self.controller = ConditionEditorControl(self)
        else:
            #pass False so Controller doesn't bind to non-existent Button
            self.controller = ConditionEditorControl(self, False)


class SetEditorControl(object):
    """This class implements a row of widgets for specifying a condition"""
    id = None
    condition = None
    condType = None
    editor = None

    
    def __init__(self, conView):
        """Setup editor control, bind to events"""
        
        #self.id = id #this will get replaced by the condition ID
        #self.condition = None
        self.editor = conView

        self.editor.btnAdd.Bind(wx.EVT_BUTTON, self.add_condition)
        self.editor.btnDel.Bind(wx.EVT_BUTTON, self.remove_set)
        
    def load_condition(self, condition):
        """
        This method accepts a condition object and loads it into the widget
        """
        self.id = condition.condID
        self.condition = condition
        #Now load any elements into appropriate controls
        
        #Must check type of column/field1 to determine what widgets to load

    def add_condition(self, evt):
        """This handles the event and sends a message with the object"""
        ind = self.editor.indentation + 30
        parentSizer = self.editor.topSizer
        pub.sendMessage('where.set_insert.condition', queryID = 0, parentSizer = parentSizer, ind = ind, panel = self.editor)

    def remove_set(self, evt):
        """
        Remove set and contained widgets
        """
        pub.sendMessage('where.remove.set', queryID = 0, parentPanel = self.editor.parent, panel = self.editor)

    def update_choice(self, evt):
        """
        This method handles the choice  with values 'any' , 'all' being updated.
        """
        pass
    
    

class ConditionEditorControl(object):
    """This class implements a row of widgets for specifying a condition"""
    id = None
    condition = None
    condType = None
    editor = None
    conditionValues = []
    
    def __init__(self, conView, top = True):
        """Set up editor control, bind to events"""
        
        #self.id = id #this will get replaced by the condition ID
        #self.condition = None
        self.editor = conView

        self.editor.btnAdd.Bind(wx.EVT_BUTTON, self.add_condition)
        self.editor.btnDel.Bind(wx.EVT_BUTTON, self.remove)
        if top == True:
            self.editor.btnSub.Bind(wx.EVT_BUTTON, self.add_sub)

    def load_condition(self, condition):
        """
        This method accepts a condition object and loads it into the widget
        """
        self.id = condition.condID
        self.condition = condition
        #Now load any elements into appropriate controls
        
        #Must check type of column/field1 to determine what widgets to load

    def add_condition(self, evt):
        """This handles the event and sends a message with the object"""
        
        sizer = self.editor.topSizer
        pub.sendMessage('where.insert.condition', queryID = 0, sizer = sizer, panel = self.editor.parent, ind = self.editor.indentation)

    def add_sub(self, evt):
        """
        This is called in the event of the editor.btnSub, or add child Set button being clicked
        """
        sizer = self.editor.topSizer
        pub.sendMessage('where.insert.sub_set', queryID = 0,  sizer = sizer, panel = self.editor.parent, ind = self.editor.indentation)


    def remove(self, evt):
        """Remove self"""
        sizer = self.editor.topSizer
        pub.sendMessage('where.remove.condition', queryID = 0, panel = self.editor.parent, condSizer = sizer)

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
