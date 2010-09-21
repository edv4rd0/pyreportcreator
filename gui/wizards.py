from wx import wizard as wiz
import wx
import os.path




class TitlePage(wiz.PyWizardPage):
    """Page for wizard, allows user to select database type to connect to."""

    def __init__(self, parent, title, controller):
        """Initialize Wizard page"""
        wiz.PyWizardPage.__init__(self, parent)
        self.next = self.prev = None
        
        self.wizardController = controller #this is to set next pages
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        self.textTitle = wx.StaticText(self, -1, title)
        self.textTitle.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.textExplain = wx.StaticText(self, -1, "Please select your database type")
        # choices
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
        """Set next page based on value of radio buttons"""
        if self.rbDBChoice_mysql.GetValue() == True:
            self.wizardController.connValues.append('mysql')
            self.next = self.wizardController.detailsPage
        elif self.rbDBChoice_postgresql.GetValue() == True:
            self.wizardController.connValues.append('postgresql')
            self.next = self.wizardController.detailsPage
        else:
            self.wizardController.connValues.append('sqlite')
            self.next = self.wizardController.sqlitePage
        return self.next

    def GetPrev(self):

        return self.prev
        

class SQLitePage(wiz.PyWizardPage):
    """Page for wizard"""

    def __init__(self, parent, title):

        wiz.PyWizardPage.__init__(self, parent)
        self.next = self.prev = None

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.titleText = wx.StaticText(self, -1, title)
        self.titleText.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.explainText = wx.StaticText(self, -1, "Please browse for and select the SQLite 3 database which you want to connect to.", size = (400,200))
        #set horizontal sizer and find sqlite file widgets
        self.sizerHoriz = wx.BoxSizer(wx.HORIZONTAL)
        self.txtFilePath = wx.TextCtrl(self, -1, 'File path here', size = (300, -1))
        self.btnFindSQLiteFile = wx.Button(self, -1, 'Browse...')
        self.sizerHoriz.Add(self.txtFilePath, 0, wx.EXPAND | wx.ALL, 5)
        self.sizerHoriz.Add(self.btnFindSQLiteFile, 0, wx.EXPAND | wx.ALL, 5)
        
        # set up main sizer
        self.sizer.Add(self.titleText, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        
        self.sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 5)
        
        self.sizer.Add(self.sizerHoriz, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        self.sizer.Add(self.explainText, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

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
            self.txtFilePath.ChangeValue(dialog.GetPath())
            self.SetNext(self.wizardCotroller.finalPage) #set next page, this might be changed to fail page if the connection fails
            
class DetailsPage(wiz.PyWizardPage):
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

        
class WizardNewDataSource(object):
    """This wizard handles the process of adding a new datasource to the profile"""
        
    def __init__(self, parent):
        """Initialize the wizard"""
        #set wizard bitmap
        try:
            bitmap = wx.Image('graphics/some-bitmap', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        except:
            bitmap = wxNullBitmap

        self.connValues = []


            
        wizard = wiz.Wizard(parent, -1, "Add a New Data Source", bitmap)
        #add pages
        self.titlePage = TitlePage(wizard, "Select Your Database Type", self)
        self.sqlitePage = SQLitePage(wizard, "SQLite Database Config")
        self.detailsPage = DetailsPage(wizard, "Database Configuration")
        self.finalPage = FinishedPage(wizard, "Finished!")
        self.failPage = FailPage(wizard, "Failed")

        #order page
        self.titlePage.SetNext(self.sqlitePage)
        self.sqlitePage.SetPrev(self.titlePage)
        self.detailsPage.SetPrev(self.titlePage)
        self.detailsPage.SetNext(self.finalPage)
        self.sqlitePage.SetNext(self.finalPage)
        #fail page and alternate orders to be defined during runtime

        wizard.GetPageAreaSizer().Add(self.titlePage)

        #bind events
        self.Bind(wiz.EVT_WIZARD_PAGE_CHANGING, self.on_page_changing)
        
        if wizard.RunWizard(self.titlePage):
            print "success"
        else:
            print "cancelled"

    def on_page_changing(self, evt):
        """Handle page changing events"""
        pass
