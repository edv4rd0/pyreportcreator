from wx import wizard as wiz
import wx
import os.path



class TitlePage(wiz.PyWizardPage):
    """Page for wizard"""

    def __init__(self, parent, title):

        wiz.PyWizardPage.__init__(self, parent)
        self.next = self.prev = None

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.textTitle = wx.StaticText(self, -1, title)
        self.textTitle.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.textExplain = wx.StaticText(self, -1, "Please select your database type")
        self.rbDBChoice_mysql = wx.RadioButton(self, -1, 'MySQL - Connect to a MySQL database', (10, 10), style=wx.RB_GROUP)
        self.rbDBChoice_postresql = wx.RadioButton(self, -1, 'PostgreSQL - Connect to a PostgreSQL database', (10, 10))
        self.rbDBChoice_sqlite = wx.RadioButton(self, -1, 'SQLite 3 - Connect to an SQLite 3 database', (10, 10))
        
        self.sizer.Add(self.textTitle, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        self.sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 5)
        self.sizer.Add(self.textExplain, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        self.sizer.Add(self.rbDBChoice_mysql, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        self.sizer.Add(self.rbDBChoice_postresql, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        self.sizer.Add(self.rbDBChoice_sqlite, 0, wx.ALIGN_LEFT | wx.ALL, 5)

    def SetNext(self, next):

        self.next = next

    def SetPrev(self, prev):

        self.prev = prev

    def GetNext(self):

        return self.next

    def GetPrev(self):

        return self.prev

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

        
class WizardNewDataSource(object):
    """This wizard handles the process of adding a new datasource to the profile"""
        
    def __init__(self, parent):
        """Initialize the wizard"""
        #set wizard bitmap
        try:
            bitmap = wx.Image('graphics/some-bitmap', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        except:
            bitmap = wxNullBitmap
            
        wizard = wiz.Wizard(parent, -1, "Add a New Data Source", bitmap)
        #add pages
        page1 = TitlePage(wizard, "Page1")
        page2 = DetailsPage(wizard, "Page2")
        page3 = DetailsPage(wizard, "Page3")
        #add content to pages
        page3.sizer.Add(wx.StaticText(page3, -1, "Last page"))
        #order page
        page1.SetNext(page2)
        page2.SetPrev(page1)
        page2.SetNext(page3)
        page3.SetPrev(page2)

        wizard.GetPageAreaSizer().Add(page1)
        
        if wizard.RunWizard(page1):
            print "Success"
        else:
            print "cancelled"
