"""Test code for a query editor"""
import wx
from pubsub import pub
import wx.lib.inspection


class WhereController(object):
    """
    This class handles the gui events etc relating to the where clause
    """
    wherePanel = None
    elementControllers = []
    
    def __init__(self):
        """Initialize stuff so events can be monitored"""
        
        frame = TestFrame(None, -1, '')
        self.whereEditor = frame.whereEditor
        self.wherePanel = self.whereEditor.panel
        #bind to events
        self.whereEditor.btnAdd.Bind(wx.EVT_BUTTON, self.add_condition)
        self.whereEditor.btnSub.Bind(wx.EVT_BUTTON, self.add_set)

        #pubsub subscriptions
        pub.subscribe(self.add_sibling_condition, 'where.insert.condition')
        pub.subscribe(self.add_child_condition, 'where.set_insert.condition')
        
    def add_condition(self, evt):
        """Add condition to top level"""
        c = ConditionEditor(self.wherePanel, 6)
        self.elementControllers.append(ConditionEditorControl(c))
        
        self.wherePanel.add_condition(c.topSizer)

    def add_set(self, evt):
        """Add condition set to top level"""

        s = SetEditor(self.wherePanel, 6)
        
        self.wherePanel.topSizer.Insert(0, s, 0, wx.EXPAND | wx.ALL)
        self.wherePanel.Layout()
        
    def add_child_set(self, object):
        pass
        
    def add_sibling_condition(self, queryID, sizer, parentSizer):
        """Handles a message from pubsub"""
        if queryID == 0:
            #get sizer and index
            szItem = parentSizer.GetItem(sizer)
            index = parentSizer.GetChildren().index(szItem)
            print index
            index += 1 #insert below element
            #setup Editor
            c = ConditionEditor(self.wherePanel, 6)
            self.elementControllers.append(ConditionEditorControl(c))
            
            parentSizer.Insert( index, c.topSizer, 0, wx.EXPAND | wx.ALL)
            self.wherePanel.Layout()

    def add_child_condition(self, queryID, parentSizer, ind):
        if queryID == 0:
            #setup Editor
            c = ConditionEditor(self.wherePanel, 6)
            self.elementControllers.append(ConditionEditorControl(c))
            
            parentSizer.Insert( 0, c.topSizer, 0, wx.EXPAND | wx.ALL)
            
            self.wherePanel.Layout()
            
            

class WhereEditor(object):
    """
    This is the class containing everything else needed in the where clause of the query.
    """
    parent = None
    panel = None
    logicChoices = [ u"all", u"any" ]
    
    def __init__(self, parent):
        """Setup"""
        self.parent = parent
        self.panel = QueryPanel(parent)
	self.topSizer = wx.BoxSizer( wx.VERTICAL )

	fgSizer3 = wx.FlexGridSizer( 1, 6, 0, 0 )
        fgSizer3.AddGrowableCol( 4,1 )
	fgSizer3.SetFlexibleDirection( wx.HORIZONTAL )
	fgSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
	
	self.stDesc1 = wx.StaticText( parent, wx.ID_ANY, u"Match", wx.DefaultPosition, wx.DefaultSize, 0 )
	self.stDesc1.Wrap( -1 )
	fgSizer3.Add( self.stDesc1, 0, wx.ALL, 5 )
	
	self.choiceLogic = wx.Choice( parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.logicChoices, 0 )
	self.choiceLogic.SetSelection( 0 )
	fgSizer3.Add( self.choiceLogic, 0, wx.ALL, 5 )
	
	self.stDesc2 = wx.StaticText( parent, wx.ID_ANY, u"of the following conditions:", wx.DefaultPosition, wx.DefaultSize, 0 )
	self.stDesc2.Wrap( -1 )
	fgSizer3.Add( self.stDesc2, 0, wx.ALL, 5 )

        fgSizer3.Add((0, 0), 1, wx.EXPAND)
	# Control Buttons
	self.btnAdd = wx.Button( parent, wx.ID_ANY, u"+", wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
	fgSizer3.Add( self.btnAdd, 0, wx.ALL| wx.ALIGN_RIGHT, 5 )
        hBoxSpacing =  wx.BoxSizer( wx.HORIZONTAL)
	
	self.btnSub = wx.Button( parent, wx.ID_ANY, u"...", wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
        hBoxSpacing.Add( self.btnSub, 0, wx.ALL | wx.ALIGN_RIGHT, 5 )
        hBoxSpacing.Add((2,-1), 0)
	fgSizer3.Add( hBoxSpacing, 0)
	self.topSizer.Add( fgSizer3, 0, wx.ALL | wx.EXPAND, 5 )
        self.topSizer.Add( self.panel, 1, wx.ALL | wx.EXPAND, 5)

    
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
    logicChoices = [ u"all", u"any" ]
    elemID = 0
    
    def __init__(self, parent, id, indentation = 0):
        """Initialise the set"""
        QueryCondEditor.__init__(self, parent, id, indentation)
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL)
        self.SetBackgroundColour('#C9C0BB')
	self.topSizer = wx.BoxSizer( wx.VERTICAL )
	fgSizer3 = wx.FlexGridSizer( 1, 7, 1, 1 )
        fgSizer3.AddGrowableCol( 4,0 )
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
	
	self.btnSub = wx.Button( self, wx.ID_ANY, u"...", wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
        fgSizer3.Add( self.btnSub, 0, wx.ALL| wx.ALIGN_RIGHT, 5 )
	
	self.topSizer.Add( fgSizer3, 0, wx.ALL | wx.EXPAND)

	self.SetAutoLayout(True)
	self.SetSizer(self.topSizer)
	self.Layout()

    def get_index_in_top_sizer(self):
        self.topSizer.GetItem(self, True)





class ConditionEditor(QueryCondEditor):
    
    operations = ['contains', 'equals', 'is in', 'not in', 'does not contain', 'not equal to']
    date__opr = ['between', 'equals', 'not equal to', 'not between']
    
    def __init__(self, parent, id, indentation = 0):
        """Initialise editor interface"""
        QueryCondEditor.__init__(self, parent, id, indentation)

        self.topSizer = wx.FlexGridSizer( 1, 5, 1, 1 )

        self.topSizer.AddGrowableCol( 1 )
	self.topSizer.SetFlexibleDirection( wx.HORIZONTAL )
	self.topSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        hBoxSizer = wx.BoxSizer( wx.HORIZONTAL )
        hBoxSizer.SetDimension(1,1,200, -1)
        if indentation > 0:
            hBoxSizer.AddSpacer(indentation, -1)
        
	self.btnDataItem = wx.Button( parent, wx.ID_ANY, u"Column...", wx.DefaultPosition, wx.DefaultSize, 0 )
	hBoxSizer.Add( self.btnDataItem, 0, wx.ALL, 5 )
	
	self.stColumn = wx.StaticText(parent, wx.ID_ANY, "Select a column", wx.DefaultPosition, wx.DefaultSize, 0 )
	self.stColumn.Wrap( -1 )
	hBoxSizer.Add( self.stColumn, 0,wx.ALL, 5 )
	
	self.choiceOperator = wx.Choice( parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.operations, 0 )
	self.choiceOperator.SetSelection( 0 )
	hBoxSizer.Add( self.choiceOperator, 0,wx.ALL, 5 )
        #add box sizer with first three widgets to grid sizer
        self.topSizer.Add(hBoxSizer, 1, wx.ALL)
	#The param widget(s)
	self.paramWidget = wx.TextCtrl( parent, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (350, -1), 0)
	self.topSizer.Add( self.paramWidget, 1, wx.EXPAND| wx.ALL, 5 )

        self.btnDel = wx.Button( parent, wx.ID_ANY, u" - ", wx.DefaultPosition, size = (40, -1))
	self.topSizer.Add( self.btnDel, 0, wx.ALL| wx.ALIGN_RIGHT, 5 )
	self.btnAdd = wx.Button( parent, wx.ID_ANY, u" + ", wx.DefaultPosition, size = (40, -1))
	self.topSizer.Add( self.btnAdd, 0, wx.ALL| wx.ALIGN_RIGHT, 5 )

        self.btnSub = wx.Button( parent, wx.ID_ANY, u"...", wx.DefaultPosition, size = (40, -1))
	self.topSizer.Add( self.btnSub, 0, wx.ALL| wx.ALIGN_RIGHT, 5 )
        
            
    def init_value_contains(self):
        """Set up value contains field"""
        self.paramWidget = wx.TextCtrl(self.parent, -1, size = (200, -1))

    def combo_operations(self, evt):
        """Handles the on click event on the operations combo box"""
        if self.CBoperator.GetValue() == 'contains':
            self.init_value_contains()

class SetEditorControl(object):
    """This class implements a row of widgets for specifying a condition"""
    id = None
    condition = None
    condType = None
    editor = None

    
    def __init__(self, conView):
        #self.id = id #this will get replaced by the condition ID
        #self.condition = None
        self.editor = conView

        self.editor.btnAdd.Bind(wx.EVT_BUTTON, self.add_condition)
        
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
        indentation += 30
        parentSizer = self.editor.topSizer
        pub.sendMessage('where.set_insert.condition', queryID = 0, parentSizer = parentSizer, ind = indentation)

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
    
    def __init__(self, conView):
        #self.id = id #this will get replaced by the condition ID
        #self.condition = None
        self.editor = conView

        self.editor.btnAdd.Bind(wx.EVT_BUTTON, self.add_condition)
        
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
        
        parentSizer = self.editor.parent.topSizer
        sizer = self.editor.topSizer
        pub.sendMessage('where.insert.condition', queryID = 0, sizer = sizer, parentSizer = parentSizer)

    def update_condition(self, evt):
        """
        This method is called in the event of the value of one of the condition widgets changing.
        It sends a pubsub request which is picked up by the query object and it then will alter the model
        """
        pass

class QueryPanel(wx.Panel):
    """The panel for a query editor"""

    def __init__( self, parent ):
	wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL| wx.SUNKEN_BORDER )
        self.SetBackgroundColour('#C9C0BB')

	self.topSizer = wx.BoxSizer( wx.VERTICAL )
        self.SetAutoLayout(True)
        self.SetSizer( self.topSizer )
	self.Layout()

    def add_condition(self, condSizer):
        """Add element to set of conditions"""
        self.topSizer.Insert(0, condSizer, 0, wx.EXPAND | wx.ALL)
        self.Layout()

    def add_set(self, condSet):
        """Add element to set of conditions"""
        self.topSizer.Insert(0, condSet, 0, wx.EXPAND | wx.LEFT | wx.RIGHT)
        self.Layout()
        
class TestFrame( wx.Frame ):
    
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)
        panel = wx.Panel(self, -1)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.whereEditor = WhereEditor(panel)
        vbox.Add(self.whereEditor.topSizer, 1, wx.EXPAND | wx.ALL, 20)
        
        panel.SetAutoLayout(True)
        panel.SetSizer(vbox)
        panel.Layout()
	self.Maximize()
        self.Centre()
        self.Show(True)


class Application(wx.App):

    def __init__(self):
        wx.App.__init__(self)

        #init objects
        self.controller = WhereController()

app = Application()
wx.lib.inspection.InspectionTool().Show()


app.MainLoop()
