import wx
import wx.lib.agw.foldpanelbar as fpb
import mainpanel

class MainToolBar(object):
    """defines the main toolbar"""
    def __init__(self, parent):
        self.mainToolbar = parent.CreateToolBar( wx.TB_HORIZONTAL, wx.ID_ANY )
        self.mainToolbar.AddLabelTool(1, u"Add a New Data Source", wx.Bitmap( u"gui/icons/db_add.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Add a New Data Source", u"Launch New Data Source Wizard", None)

        self.mainToolbar.Realize()

class MainMenu(object):
    """Define the main menubar"""

    def __init__(self, parent):
        """Initialize"""
        self.menuBar = wx.MenuBar( 0 )
        # File Menu
        self.menuFile = wx.Menu()
        self.menuFileNewProject = wx.MenuItem( self.menuFile, wx.ID_ANY, u"&New Project", wx.EmptyString, wx.ITEM_NORMAL )
        self.menuFile.AppendItem( self.menuFileNewProject )
        
        self.menuFileOpen = wx.MenuItem( self.menuFile, wx.ID_ANY, u"&Open Project", wx.EmptyString, wx.ITEM_NORMAL )
        self.menuFile.AppendItem( self.menuFileOpen )
        
        self.menuFileSaveAs = wx.MenuItem( self.menuFile, wx.ID_ANY, u"Save Project As", wx.EmptyString, wx.ITEM_NORMAL )
        self.menuFile.AppendItem( self.menuFileSaveAs )
        
        self.menuFileQuit = wx.MenuItem( self.menuFile, wx.ID_ANY, u"E&xit", wx.EmptyString, wx.ITEM_NORMAL )
        self.menuFile.AppendItem( self.menuFileQuit )
        
        self.menuBar.Append( self.menuFile, u"&File" ) 
        # Project menu
        self.menuProject = wx.Menu()
        self.menuBar.Append( self.menuProject, u"&Project" )
        self.menuProjectNewQuery = wx.MenuItem( self.menuFile, wx.ID_ANY, u"&New Query", wx.EmptyString, wx.ITEM_NORMAL )
        self.menuProject.AppendItem( self.menuProjectNewQuery )
        # Help menu
        self.menuHelp = wx.Menu()
        self.menuHelpAbout = wx.MenuItem( self.menuHelp, wx.ID_ANY, u"&About", wx.EmptyString, wx.ITEM_NORMAL )
        self.menuHelp.AppendItem( self.menuHelpAbout )
        
        self.menuBar.Append( self.menuHelp, u"&Help" ) 
        # Set Menubar
        parent.SetMenuBar( self.menuBar )

#----------------------------------------------------------------------------------#

class DataPanel(object):
    """This defines the data object panel and it's presentation"""

    def __init__(self, foldb):
        """Set up layout"""
        self.panelDataObjects = foldb.AddFoldPanel("Data Objects")

        self.panel = wx.Panel(self.panelDataObjects, -1, style=wx.SUNKEN_BORDER)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.panel.SetSizer(self.sizer)

        self.treeCtrlDataItems = wx.TreeCtrl(self.panel, -1, size = (-1,250), style = wx.TR_HIDE_ROOT | wx.EXPAND | wx.ALL | wx.TR_HAS_BUTTONS)
        self.root = self.treeCtrlDataItems.AddRoot('root')
        self.sizer.Add(self.treeCtrlDataItems, 1, wx.EXPAND, 0)
        self.sizer.Fit(self.panel)
        self.sizer.SetSizeHints(self.panel)
        self.sizer.Layout()
        
        foldb.AddFoldPanelWindow(self.panelDataObjects, self.panel, wx.EXPAND | fpb.FPB_ALIGN_WIDTH)
            
#-----------------------------------------------------------------------#

class SidePanel(wx.Panel):
    """Defines the layout of the sidepanel which includes treeviews in foldpanels"""

    def __init__(self, parent):
        
        wx.Panel.__init__( self, parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL | wx.EXPAND )
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.fpb = fpb.FoldPanelBar(parent, 1, style = fpb.FPB_HORIZONTAL | wx.EXPAND)
        # data object bar
        self.dataPanel = DataPanel(self.fpb) #initialize Data Panel
        # profile objects
        self.panelProfile = self.fpb.AddFoldPanel("Profile Objects")
        self.treeProfileObjects = wx.TreeCtrl(self.panelProfile, 1, size = (-1, 250), style = wx.TR_HIDE_ROOT |  wx.TR_HAS_BUTTONS)
        w2 = self.fpb.AddFoldPanelWindow(self.panelProfile, self.treeProfileObjects, wx.EXPAND | fpb.FPB_ALIGN_WIDTH)
        self.sizer.Add(self.fpb, 1, wx.EXPAND)
        #self.sizer.Add(self.panelProfile, 1, wx.EXPAND)
        self.SetSizer(self.sizer)


class MainFrame ( wx.Frame ):
    """This is the main frame of the application"""
    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Query Creator", pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
               
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
           
        bSizer1 = wx.BoxSizer( wx.HORIZONTAL )
                
        self.splitWindow = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D | wx.SP_BORDER )
        self.splitWindow.SetMinimumPaneSize(1)
        #just some presentation related events which need handling
        self.splitWindow.Bind( wx.EVT_IDLE, self.splitWindowOnIdle )
        self.splitWindow.Bind(wx.EVT_SPLITTER_DCLICK, self.dclick)
        
        self.sidePanel = SidePanel(self.splitWindow)
        
        #end left panel contents
        self.splitPanelRight = wx.Panel( self.splitWindow, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer2 = wx.BoxSizer( wx.VERTICAL )

        self.splitPanelRight.SetMinSize((600, -1))
        #The editor ---------------
        self.mainNoteBook = mainpanel.MainNotebook(self.splitPanelRight)
        bSizer2.Add( self.mainNoteBook, 1, wx.EXPAND |wx.ALL, 5 )
        
        self.splitPanelRight.SetSizer( bSizer2 )
        
        self.splitPanelRight.Layout()
        bSizer2.Fit( self.splitPanelRight )
        self.splitWindow.SplitVertically( self.sidePanel, self.splitPanelRight, 200 )
        bSizer1.Add( self.splitWindow, 1, wx.EXPAND, 5 )
              
        self.SetSizer( bSizer1 )
        self.Layout()
        self.mainStatusBar = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
               
        self.Centre( wx.BOTH )

    def dclick(self, evt):
        """Need to veto the event which closes one window"""
        if self.splitWindow.GetSashPosition() == 1:
            self.splitWindow.SetSashPosition(200)
        else:
            self.splitWindow.SetSashPosition(1)
        evt.Veto()
        
    def __del__( self ):
        pass
        
    def splitWindowOnIdle( self, evt):
        self.splitWindow.SetSashPosition(200)
        self.splitWindow.Unbind(wx.EVT_IDLE)
