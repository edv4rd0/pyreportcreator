from wx import wizard as wiz
import wx
import os.path
import string
from pyreportcreator.datahandler import datahandler
#TODO: Cleanup all print statements

def establish_sqlite_connection(address):
    """Establish an SQLite connection."""
    
    print "trying to establish a connection"
    print address
    import sys
    i = ""
    if sys.platform != "win32":
        try:
            i = string.rindex(address, "/")
            print i
            print "\n" 
        except ValueError:
            print ValueError
    else:
        try:
            i = string.rindex(address, "\\")
        except ValueError:
            return ValueError
    print i
    name = address[i:]
    address = address[:i+1]
    connID = datahandler.ConnectionManager.CreateNewDataConnection(u"sqlite", address, name)
    if connID != False:
        if datahandler.DataHandler.add(connID):
            return (connID, name)
        else:
            print "fail"
            return False
    else:
        print "connection failed "+ address + " " + name
        return False

#-------------------------------------------------------#

class TitlePage(wiz.PyWizardPage):
    """Page for wizard, allows user to select database type to connect to."""

    def __init__(self, parent, title, controller):
        """Initialize Wizard page"""
        wiz.PyWizardPage.__init__(self, parent)
        self.next = self.prev = None
        self.wizardControl = controller
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        self.textTitle = wx.StaticText(self, -1, title)
        self.textTitle.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.textExplain = wx.StaticText(self, -1, "Please select your database type")
        
        # choices (radio buttons)
        # Cleanup: make first button actually be selected and not just look like it is.
        self.rbDBChoice_mysql = wx.RadioButton(self, -1, 'MySQL - Connect to a MySQL database', (10, 10), style=wx.RB_GROUP)
        self.rbDBChoice_postgresql = wx.RadioButton(self, -1, 'PostgreSQL - Connect to a PostgreSQL database', (10, 10))
        self.rbDBChoice_sqlite = wx.RadioButton(self, -1, 'SQLite 3 - Connect to an SQLite 3 database', (10, 10))

        # set sizer
        self.sizer.Add(self.textTitle, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        self.sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 5)
        self.sizer.Add(self.textExplain, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        self.sizer.Add(self.rbDBChoice_mysql, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        self.sizer.Add(self.rbDBChoice_postgresql, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        self.sizer.Add(self.rbDBChoice_sqlite, 0, wx.ALIGN_LEFT | wx.ALL, 5)

    def SetNext(self, next):

        self.next = next

    def SetPrev(self, prev):

        self.prev = prev

    def GetNext(self):
        """Determines which page to load next"""
        if self.rbDBChoice_mysql.GetValue() == True:
            self.wizardControl.connValues['dbtype'] = 'mysql'
            self.next = self.wizardControl.detailsPage
        elif self.rbDBChoice_postgresql.GetValue() == True:
            self.wizardControl.connValues['dbtype'] = 'postgresql'
            self.next = self.wizardControl.detailsPage
        else:
            self.wizardControl.connValues['dbtype'] = 'sqlite'
            self.next = self.wizardControl.sqlitePage

        return self.next

    def GetPrev(self):

        return self.prev

#-------------------------------------------------------#

class SQLitePage(wiz.PyWizardPage):
    """Page for wizard"""

    def __init__(self, parent, title):

        wiz.PyWizardPage.__init__(self, parent)
        self.next = self.prev = None

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.stTitle = wx.StaticText(self, -1, title)
        self.stTitle.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.stExplaination = wx.StaticText(self, -1, "Please browse for and select the SQLite 3 database which you want to connect to.", size = (400,200))
        #set horizontal sizer and find sqlite file widgets
        self.sizerHoriz = wx.BoxSizer(wx.HORIZONTAL)
        self.tcFilePath = wx.TextCtrl(self, -1, 'File path here', size = (300, -1))
        self.btnFindSQLiteFile = wx.Button(self, -1, 'Browse...')
        self.sizerHoriz.Add(self.tcFilePath, 0, wx.EXPAND | wx.ALL, 5)
        self.sizerHoriz.Add(self.btnFindSQLiteFile, 0, wx.EXPAND | wx.ALL, 5)
        
        # set up main sizer
        self.sizer.Add(self.stTitle, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        
        self.sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 5)
        
        self.sizer.Add(self.sizerHoriz, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        self.sizer.Add(self.stExplaination, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

        # bind events
        self.btnFindSQLiteFile.Bind(wx.EVT_BUTTON, self.GetSqlitePath)
        

    def SetNext(self, next):

        self.next = next

    def SetPrev(self, prev):

        self.prev = prev

    def GetNext(self):
        
        return self.next

    def GetPrev(self):

        return self.prev
    
    def GetSqlitePath(self, evt):
        """Create find file dialog and then load path into textbox and append it
        to the list of database connection params"""
        dialog = wx.FileDialog(self, "Choose a database file...", os.getcwd(), "", "*", wx.OPEN | wx.HIDE_READONLY)
        if dialog.ShowModal() == wx.ID_OK:
            self.tcFilePath.SetValue(dialog.GetPath())

#-------------------------------------------------------#

class DetailsPage(wiz.PyWizardPage):
    """MySQL or Postgresql configuration page"""

    def __init__(self, parent, title):

        wiz.PyWizardPage.__init__(self, parent)
        self.next = self.prev = None
		
        vBoxSizerTop = wx.BoxSizer( wx.VERTICAL ) #top level box sizer
        
        fgsConnConf = wx.FlexGridSizer( 2, 2, 0, 0 )
	fgsConnConf.SetFlexibleDirection( wx.BOTH )
	fgsConnConf.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
	self.m_bitmap1 = wx.StaticBitmap( self, wx.ID_ANY, wx.Bitmap( u"../../../Downloads/logo_mysql_sun_a.gif", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
	fgsConnConf.Add( self.m_bitmap1, 0, wx.ALL, 5 )
		
	self.stHeading = wx.StaticText( self, wx.ID_ANY, u"Configure Database Connection", wx.DefaultPosition, wx.DefaultSize, 0 )
	self.stHeading.Wrap( -1 )
	fgsConnConf.Add( self.stHeading, 0, wx.ALL, 5 )
	
	self.stServerAddress = wx.StaticText( self, wx.ID_ANY, u"Server Address", wx.DefaultPosition, wx.DefaultSize, 0 )
	self.stServerAddress.Wrap( -1 )
	fgsConnConf.Add( self.stServerAddress, 0, wx.ALL, 5 )
	
	self.tcServerAddress = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 300,-1 ), 0 )
	fgsConnConf.Add( self.tcServerAddress, 0, wx.ALL, 5 )
		
	self.stPort = wx.StaticText( self, wx.ID_ANY, u"Port", wx.DefaultPosition, wx.DefaultSize, 0 )
	self.stPort.Wrap( -1 )
	fgsConnConf.Add( self.stPort, 0, wx.ALL, 5 )
		
	self.tcPort = wx.TextCtrl( self, wx.ID_ANY, u"3306", wx.DefaultPosition, wx.DefaultSize, 0 )
	self.tcPort.SetMaxLength( 4 ) 
	fgsConnConf.Add( self.tcPort, 0, wx.ALL, 5 )
		
	self.stDatabaseName = wx.StaticText( self, wx.ID_ANY, u"Database Name", wx.DefaultPosition, wx.DefaultSize, 0 )
	self.stDatabaseName.Wrap( -1 )
	fgsConnConf.Add( self.stDatabaseName, 0, wx.ALL, 5 )
		
	self.tcDatabaseName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 300,-1 ), 0 )
	fgsConnConf.Add( self.tcDatabaseName, 0, wx.ALL, 5 )
		
	vBoxSizerTop.Add( fgsConnConf, 1, wx.EXPAND, 5 )

        # Username and password area
 	sbsUserCred = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"User Credentials" ), wx.VERTICAL )
		
	fgsUserCred = wx.FlexGridSizer( 2, 2, 0, 0 )
	fgsUserCred.SetFlexibleDirection( wx.BOTH )
	fgsUserCred.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
	
	self.stUserName = wx.StaticText( self, wx.ID_ANY, u"User Name", wx.DefaultPosition, wx.DefaultSize, 0 )
	self.stUserName.Wrap( -1 )
	fgsUserCred.Add( self.stUserName, 0, wx.ALL, 5 )
		
	self.tcUserName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 250,-1 ), wx.TE_DONTWRAP )
	fgsUserCred.Add( self.tcUserName, 0, wx.ALL, 5 )
	
	self.stPass = wx.StaticText( self, wx.ID_ANY, u"Password", wx.DefaultPosition, wx.DefaultSize, 0 )
	self.stPass.Wrap( -1 )
	fgsUserCred.Add( self.stPass, 0, wx.ALL, 5 )
		
	self.tcPass = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 250,-1 ), wx.TE_DONTWRAP|wx.TE_PASSWORD )
	fgsUserCred.Add( self.tcPass, 0, wx.ALL, 5 )
		
	sbsUserCred.Add( fgsUserCred, 1, wx.EXPAND, 5 )
		
	vBoxSizerTop.Add( sbsUserCred, 1, wx.EXPAND, 5 )
		
	self.SetSizer( vBoxSizerTop )

 

    def SetNext(self, next):

        self.next = next

    def SetPrev(self, prev):

        self.prev = prev

    def GetNext(self):

        return self.next

    def GetPrev(self):

        return self.prev

#-------------------------------------------------------#

class FinishedPage(wiz.PyWizardPage):
    """Page for wizard"""

    def __init__(self, parent, title):

        wiz.PyWizardPage.__init__(self, parent)
        self.next = self.prev = None

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.titleText = wx.StaticText(self, -1, title)
        self.titleText.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        
        
        self.sizer.Add(self.titleText, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        self.sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 5)


    def SetNext(self, next):

        self.next = next

    def SetPrev(self, prev):

        self.prev = prev

    def GetNext(self):

        return self.next

    def GetPrev(self):

        return self.prev

#-------------------------------------------------------#

class FailPage(wiz.PyWizardPage):
    """Page for wizard"""

    def __init__(self, parent, title):

        wiz.PyWizardPage.__init__(self, parent)
        self.next = self.prev = None

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.titleText = wx.StaticText(self, -1, title)
        self.titleText.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        
        
        self.sizer.Add(self.titleText, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        self.sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 5)


    def SetNext(self, next):

        self.next = next

    def SetPrev(self, prev):

        self.prev = prev

    def GetNext(self):

        return self.next

    def GetPrev(self):

        return self.prev

#-------------------------------------------------------#
        
class WizardNewDataSource(object):
    """This wizard handles the process of adding a new datasource to the profile"""
        
    def __init__(self, parent):
        """Initialize the wizard"""
        #set wizard bitmap
        try:
            bitmap = wx.Image('graphics/some-bitmap', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        except:
            bitmap = wxNullBitmap

        self.connValues = dict()
            
        wizard = wiz.Wizard(parent, -1, "Add a New Data Source", bitmap)
        #add pages
        self.titlePage = TitlePage(wizard, "Select Your Database Type", self)
        self.sqlitePage = SQLitePage(wizard, "SQLite Database Config")
        self.detailsPage = DetailsPage(wizard, "Database Configuration")
        self.finalPage = FinishedPage(wizard, "Finished!")
        self.failPage = FailPage(wizard, "Failed")

        #order page
        self.titlePage.SetNext(self.detailsPage)
        self.sqlitePage.SetPrev(self.titlePage)
        self.detailsPage.SetPrev(self.titlePage)
        self.detailsPage.SetNext(self.finalPage)
        self.sqlitePage.SetNext(self.finalPage)
        #fail page and alternate orders to be defined during runtime

        wizard.GetPageAreaSizer().Add(self.titlePage)

        #bind events
        self.sqlitePage.Bind(wiz.EVT_WIZARD_PAGE_CHANGING, self.on_changing_sqlite)
        #self.sqlitePage.Bind(wx.EVT_TEXT(id, func))
        if wizard.RunWizard(self.titlePage):
            print "success"
        else:
            print "cancelled"

    def on_changing_sqlite(self, evt):
        page = evt.GetPage()
        if page.tcFilePath.IsEmpty() == True:
            evt.Veto()
        else:
            self.connValues['address'] = page.tcFilePath.GetValue()
            establish_sqlite_connection(self.connValues['address'])
