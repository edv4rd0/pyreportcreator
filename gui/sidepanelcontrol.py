"""This is the control code for the side panel"""
from pyreportcreator.datahandler import datahandler
from pyreportcreator.profile import profile
from pubsub import pub
import wx

class DataPanelControl(object):
    """This controls events connected with the data panel/treeview"""

    def __init__(self, view, profile):
        """Initialize and bind to events"""
        self.view = view
        self.dataIndex = dict()
        self.profile = profile
        self.tree = self.view.treeCtrlDataItems
        #subscribe to data add events
        pub.subscribe(self.update_view, 'databaseadded')

    def check_if_item_not_exist(self, connID):
        """
        Checks if the database is already loaded.
        If not: return False.
        Else: delete all children and return Item
        """
        try:
            return self.dataIndex[connID]
        except KeyError:
            return False #not in there

    def update_view(self, connID):
        """This grabs the connection ID and populates the view with the data information"""
        print 1
        try:
            name = self.profile.connections[connID][2]
        except AttributeError:
            name = connID
            print AttributeError, "update_view"
        item = self.check_if_item_not_exist(connID) #false if item not exist, item if it does
        if item:
            d = item
            self.tree.DeleteChildren(item)
            
        else:
            d = self.tree.AppendItem(self.view.root, name + str(connID))
            self.dataIndex[connID] = d #need to keep data index as an easy way of insuring we don't display the same database twice
            
        tables = datahandler.DataHandler.get_tables(connID)
        for i in tables:
            j = self.tree.AppendItem(d, i)
            self.tree.SetPyData(j, (connID, i))
            
        (child, cookie) = self.tree.GetFirstChild(d)
        while child.IsOk(): 
            # do something with child
            c = self.tree.GetItemData(child).GetData()
            columns = datahandler.DataHandler.get_columns(c[0], c[1])
            for k in columns:
                if k[2]:
                    colDesc = k[0] + "[PK]"
                else:
                    colDesc = k[0]
                    
                f = self.tree.AppendItem(child, colDesc)
                self.tree.SetPyData(f, (c[0], c[1], k))
            (child, cookie) = self.tree.GetNextChild(d, cookie)



class ProfilePanelControl(object):
    """This controls events connected with the tree control (mostly) in the sidepanel class"""

    def __init__(self, view, profile):
        """Initialize and bind to events"""
        self.view = view
        self.documentIndex = dict()
        self.profile = profile
        self.tree = self.view
        self.root = self.tree.AddRoot("root")
        self.queryNode = self.tree.AppendItem(self.root, "Queries")
        self.tree.SetPyData(self.queryNode, 'query')
        self.reportNode = self.tree.AppendItem(self.root, "Reports")
        self.tree.SetPyData(self.reportNode, 'report')
        #bind to widget events
        self.tree.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.right_click)
        self.tree.Bind(wx.EVT_LEFT_DCLICK, self.open_doc)
        
        #subscribe to data add events
        pub.subscribe(self.add_document, 'newdocument')

    def right_click(self, evt):
        pass

    def open_doc(self, evt):
        item = self.tree.GetSelection()
        data = self.tree.GetItemData(item).GetData()
        if data not in ('query', 'report'):
            docType = self.tree.GetItemData(self.tree.GetItemParent(item)).GetData()
            pub.sendMessage('open_document', docType = docType, documentID = data)
            

    def add_document(self, name, docId, docType):
        """This handles a new document added message"""
        if docType == 'query':
            parent = self.queryNode
        else:
            parent = self.reportNode
        item = self.tree.AppendItem(parent, name)
        self.tree.SetPyData(item, docId)
