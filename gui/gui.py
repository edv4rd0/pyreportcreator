# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Sep 20 2010)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx

###########################################################################
## Class mainFrame
###########################################################################

class MainToolBar(object):
    """defines the main toolbar"""
    def __init__(self, parent):
        self.mainToolbar = parent.CreateToolBar( wx.TB_HORIZONTAL, wx.ID_ANY )
	self.mainToolbar.AddLabelTool(1, u"Add a New Data Source", wx.Bitmap( u"icons/db_add.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Add a New Data Source", u"Launch New Data Source Wizard", None)

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
	
	self.menuFileOpen = wx.MenuItem( self.menuFile, wx.ID_ANY, u"&Open...", wx.EmptyString, wx.ITEM_NORMAL )
	self.menuFile.AppendItem( self.menuFileOpen )
	
	self.menuFileSave = wx.MenuItem( self.menuFile, wx.ID_ANY, u"&Save", wx.EmptyString, wx.ITEM_NORMAL )
	self.menuFile.AppendItem( self.menuFileSave )
	
	self.menuFileSaveAs = wx.MenuItem( self.menuFile, wx.ID_ANY, u"Save As", wx.EmptyString, wx.ITEM_NORMAL )
	self.menuFile.AppendItem( self.menuFileSaveAs )
	
	self.menuFileQuit = wx.MenuItem( self.menuFile, wx.ID_ANY, u"E&xit", wx.EmptyString, wx.ITEM_NORMAL )
	self.menuFile.AppendItem( self.menuFileQuit )
	
	self.menuBar.Append( self.menuFile, u"&File" ) 
	# Project menu
	self.menuProject = wx.Menu()
	self.menuBar.Append( self.menuProject, u"&Project" ) 
	# Help menu
	self.menuHelp = wx.Menu()
	self.menuHelpAbout = wx.MenuItem( self.menuHelp, wx.ID_ANY, u"&About", wx.EmptyString, wx.ITEM_NORMAL )
	self.menuHelp.AppendItem( self.menuHelpAbout )
	
	self.menuBar.Append( self.menuHelp, u"&Help" ) 
	# Set Menubar
	parent.SetMenuBar( self.menuBar )
		

class SidePanel(object):
    """Defines the layout of the sidepanel which includes treeviews in foldpanels"""

    def __init__(self, parent, sizer):
        import wx.lib.agw.foldpanelbar as fpb
        #self.text_ctrl_1 = wx.TextCtrl(parent,-1,style=wx.TE_MULTILINE)

        self.fpb = fpb.FoldPanelBar(parent,-1, style=fpb.FPB_HORIZONTAL)
        self.fold_panel = self.fpb.AddFoldPanel("Thing")
        self.thing = wx.TextCtrl(self.fold_panel,-1, size=(400,-1), style=wx.TE_MULTILINE)
        self.fpb.AddFoldPanelWindow(self.fold_panel, self.thing)

        #sizer.Add(self.text_ctrl_1,1,wx.EXPAND)
        sizer.Add(self.fpb,1,wx.EXPAND)

        parent.SetSizer(sizer)


class MainFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Edward's Report Creator", pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer1 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.splitWindow = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D )
		self.splitWindow.Bind( wx.EVT_IDLE, self.splitWindowOnIdle )
		
		self.splitPanelLeft = wx.Panel( self.splitWindow, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer3 = wx.BoxSizer( wx.VERTICAL )
		
		self.splitPanelLeft.SetSizer( bSizer3 )
		self.splitPanelLeft.Layout()
		bSizer3.Fit( self.splitPanelLeft )
		#left panel contents added in here
		self.sidePanel = SidePanel(self.splitPanelLeft, bSizer3)
		#end left panel contents
		self.splitPanelRight = wx.Panel( self.splitWindow, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer2 = wx.BoxSizer( wx.VERTICAL )
		
		self.mainNoteBook = wx.Notebook( self.splitPanelRight, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		
		bSizer2.Add( self.mainNoteBook, 1, wx.EXPAND |wx.ALL, 5 )
		
		self.splitPanelRight.SetSizer( bSizer2 )
		self.splitPanelRight.Layout()
		bSizer2.Fit( self.splitPanelRight )
		self.splitWindow.SplitVertically( self.splitPanelLeft, self.splitPanelRight, 200 )
		bSizer1.Add( self.splitWindow, 1, wx.EXPAND, 5 )
		
		self.SetSizer( bSizer1 )
		self.Layout()
		self.mainStatusBar = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
		

		
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	
	def splitWindowOnIdle( self, event ):
		self.splitWindow.SetSashPosition( 200 )
		self.splitWindow.Unbind( wx.EVT_IDLE )
