"""Test code for a query editor"""
import wx
#from pubsub import pub
import wx.lib.inspection



class QueryCondEditor(object):
    """
    This is the abstract class for the editor for query conditions
    """
    controller = None
    parent = None
    id = None
    indent = None

    def __init__(self, parent, id, indentation = 0):
        """
        initialise the editor

        The 'indentation' param is for specifying how many spacers to put in.
        """
        self.parent = parent
        self.controller = ConditionEditorControl(id)
        self.indent = indentation

    def add_element(self, evt):
        """Add element to set of conditions"""
        pass

    def add_sub_element(self, evt):
        """Add a sub element to conditions"""
        pass
    

class SetEditor(QueryCondEditor, wx.Panel):
    logicChoices = [ u"all", u"any" ]
    elemID = 0
    
    def __init__(self, parent, id, indentation = 0):
        """Initialise the set"""
        QueryCondEditor.__init__(self, parent, id, indentation)
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL)
        self.SetBackgroundColour('#C9C0BB')
	self.setSizer = wx.BoxSizer( wx.VERTICAL )
	fgSizer3 = wx.FlexGridSizer( 1, 7, 0, 0 )
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
	self.btnDel = wx.Button( self, wx.ID_ANY, u"-", wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
	fgSizer3.Add( self.btnDel, 0, wx.ALL| wx.ALIGN_RIGHT, 5 )
	
	self.btnAdd = wx.Button( self, wx.ID_ANY, u"+", wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
	fgSizer3.Add( self.btnAdd, 0, wx.ALL| wx.ALIGN_RIGHT, 5 )
	
	self.btnSub = wx.Button( self, wx.ID_ANY, u"...", wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
        fgSizer3.Add( self.btnSub, 0, wx.ALL| wx.ALIGN_RIGHT, 5 )
	
	self.setSizer.Add( fgSizer3, 0, wx.ALL | wx.EXPAND, 5 )
        self.btnAdd.Bind(wx.EVT_BUTTON, self.add_sub_element)
	self.SetAutoLayout(True)
	self.SetSizer(self.setSizer)
	self.Layout()

    def add_element(self, evt):
        """Add element to set of conditions"""
        pass

    def add_sub_element(self, evt):
        """Add a sub element to conditions"""
        c = ConditionEditor(self, 6)
        self.setSizer.Insert(1, c.topSizer, 0, wx.EXPAND | wx.ALL)
        self.Layout()



class ConditionEditor(QueryCondEditor):
    
    operations = ['contains', 'equals', 'is in', 'not in', 'does not contain', 'not equal to']
    date__opr = ['between', 'equals', 'not equal to', 'not between']

    
    def __init__(self, parent, id, indentation = 0):
        """Initialise editor interface"""
        QueryCondEditor.__init__(self, parent, id, indentation)

        self.topSizer = wx.FlexGridSizer( 1, 7, 1, 1 )
        self.topSizer.AddGrowableCol( 3 )
	self.topSizer.SetFlexibleDirection( wx.HORIZONTAL )
	self.topSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        #self.topSizer.AddSpacer(40, -1)
		
	self.btnDataItem = wx.Button( parent, wx.ID_ANY, u"Column...", wx.DefaultPosition, wx.DefaultSize, 0 )
	self.topSizer.Add( self.btnDataItem, 1, wx.ALL, 5 )
	
	self.m_staticText4 = wx.StaticText(parent, wx.ID_ANY, "Select a column", wx.DefaultPosition, wx.DefaultSize, 0 )
	self.m_staticText4.Wrap( -1 )
	self.topSizer.Add( self.m_staticText4, 1, wx.ALL, 5 )
	
	self.choiceOperator = wx.Choice( parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.operations, 0 )
	self.choiceOperator.SetSelection( 0 )
	self.topSizer.Add( self.choiceOperator, 1, wx.ALL, 5 )
	#The param widget(s)
	self.paramWidget = wx.TextCtrl( parent, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (-1, -1), 0)
	self.topSizer.Add( self.paramWidget, 1, wx.EXPAND| wx.ALL, 5 )

        self.btnDel = wx.Button( parent, wx.ID_ANY, u" - ", wx.DefaultPosition, size = (40, -1))
	self.topSizer.Add( self.btnDel, 1, wx.ALL| wx.ALIGN_RIGHT, 5 )
	self.btnAdd = wx.Button( parent, wx.ID_ANY, u" + ", wx.DefaultPosition, size = (40, -1))
	self.topSizer.Add( self.btnAdd, 1, wx.ALL| wx.ALIGN_RIGHT, 5 )

        self.btnSub = wx.Button( parent, wx.ID_ANY, u"...", wx.DefaultPosition, size = (40, -1))
	self.topSizer.Add( self.btnSub, 1, wx.ALL| wx.ALIGN_RIGHT, 5 )
        
            
    def compile_values(self):
        """Grab the value of each control and return it"""
        pass

    def init_value_contains(self):
        """Set up value contains field"""
        self.paramWidget = wx.TextCtrl(self.parent, -1, size = (200, -1))

    def combo_operations(self, evt):
        """Handles the on click event on the operations combo box"""
        if self.CBoperator.GetValue() == 'contains':
            self.init_value_contains()
            
            
    

class ConditionEditorControl(object):
    """This class implements a row of widgets for specifying a condition"""
    id = None
    condition = None
    condType = None
    editor = None
    
    def __init__(self, id):
        self.id = id #this will get replaced by the condition ID
        self.condition = None
        
    def load_condition(self, condition):
        """
        This method accepts a condition object and loads it into the widget
        """
        self.id = condition.condID
        self.condition = condition
        #Now load any elements into appropriate controls
        
        #Must check type of column/field1 to determine what widgets to load


class QueryPanel(wx.Panel):
    """The panel for a query editor"""
    editors = []

    def __init__( self, parent ):
	wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL| wx.SUNKEN_BORDER )


	bSizer1 = wx.BoxSizer( wx.VERTICAL )
        bSizer1.Add(SetEditor(self, 1),  1,  wx.ALL| wx.EXPAND, 5)
        self.SetSizer( bSizer1 )
        
	self.Layout()
        
	
        
class TestFrame( wx.Frame ):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)
        panel = wx.Panel(self, -1)
        vbox = wx.BoxSizer(wx.VERTICAL)
        subPanel = QueryPanel(panel)
        subPanel.SetBackgroundColour('#C9C0BB')
        vbox.Add(subPanel, 1, wx.EXPAND | wx.ALL, 20)
        
        panel.SetAutoLayout(True)
        panel.SetSizer(vbox)
        panel.Layout()
	self.Maximize()
        self.Centre()
        self.Show(True)


def editor_factory(parent, parentSizer, listOfEditors):
    pass


app = wx.App()
wx.lib.inspection.InspectionTool().Show()
TestFrame(None, -1, '')
app.MainLoop()
