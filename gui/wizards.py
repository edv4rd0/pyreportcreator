from wx import wizard
import wx
import os.path

class TitledPage(wizard.WizardPageSimple):
    """Generic titled page for a wizard"""

    def __init__(self, parent, title):

        wizard.WizardPageSimple.__init__(self, parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.titleText = wx.StaticText(self, -1, title)
        self.titleText.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.sizer.Add(self.titleText, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        self.sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 5)
        
class WizardNewDataSource(object):
    """This wizard handles the process of adding a new datasource to the profile"""
        
    def __init__(self, parent):
        """Initialize the wizard"""
        self.wizard = wizard.Wizard(parent, -1, "Add a New Data Source")
        #add pages
        self.page1 = TitledPage(self.wizard, "Page1")
        self.page2 = TitledPage(self.wizard, "Page2")
        self.page3 = TitledPage(self.wizard, "Page3")
        #add content to pages
        self.page1.sizer.Add(wx.StaticText(self.page1, -1, "Please select your database type"))
        self.page3.sizer.Add(wx.StaticText(self.page3, -1, "Last page"))
        #order pages
        wizard.WizardPageSimple_Chain(self.page1, self.page2)
        wizard.WizardPageSimple_Chain(self.page2, self.page3)

        if self.wizard.RunWizard(self.page1):
            print "Success"
