"""This is the control code for the side panel"""
from pyreportcreator.datahandler import datahandler
from pyreportcreator.profile import profile
from pyreportcreator.gui import gui
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
        #bind to events
        self.tree.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.context_menu)

        #subscribe to data add events
        pub.subscribe(self.update_view, 'databaseadded')
        pub.subscribe(self.db_reconnected, 'connectionfixed')
        pub.subscribe(self.db_disconnected, 'disconnected')

    def context_menu(self, evt):
        if self.tree.GetItemData(evt.GetItem()).GetData()[1] == "disconnected":
            self.tree.PopupMenu(gui.DataContextMenu(self), evt.GetPoint())

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
        
    def db_disconnected(self, connID):
        """Update view to reflect the fact that one data connection is offline"""
        root = self.tree.GetRootItem()
        print "disconnected", connID
        (child, cookie) = self.tree.GetFirstChild(root)
        while child.IsOk():
            print self.tree.GetData(child).GetData()[0]
            if self.tree.GetData(child).GetData()[0] == connID:
                self.tree.SetPyData(child, (connID, "disconnected"))
                text = self.tree.GetItemText(child)
                self.tree.SetItemText(child, "[off] " + text)
                print "changed text"
                break
            (child, cookie) = self.tree.GetNextChild(root, cookie)

    def db_reconnected(self, connID):
        """Update view to reflect fact that db has reconnected"""
        root = self.tree.GetRootItem()
        (child, cookie) = self.tree.GetFirstChild(sroot)
        while child.IsOk():
            if self.tree.GetData(child).GetData()[0] == connID:
                self.tree.SetPyData(child, (connID, "connected"))
                text = self.tree.GetItemText(child)
                self.tree.SetItemText(child, text[6:])
                break
            (child, cookie) = self.tree.GetNextChild(root, cookie)

    def update_view(self, connID, connected = True):
        """This grabs the connection ID and populates the view with the data information"""
 
        try:
            name = self.profile.connections[connID][2]
            address = self.profile.connections[connID][1]
        except AttributeError:
            name = connID
            print AttributeError, "update_view"
        item = self.check_if_item_not_exist(connID) #false if item not exist, item if it does
        if item:
            d = item
            self.tree.DeleteChildren(item)
            
        else:
            if connected == True:
                d = self.tree.AppendItem(self.view.root, name + "@" + address)
                self.tree.SetPyData(d, (connID, "connected"))
            else:
                d = self.tree.AppendItem(self.view.root, "[off] " + name + "@" + address)
                self.tree.SetPyData(d, (connID, "disconnected"))
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
        pub.subscribe(self.remove_query, 'removequery')
        pub.subscribe(self.name_changed, 'namechanged')


    def remove_query(self, docId):
        """Remove listing of query document in tree ctrl"""
        (child, cookie) = self.tree.GetFirstChild(self.queryNode)
        while child.IsOk(): 
            # do something with child
            c = self.tree.GetItemData(child).GetData()
            print c, "query doc data"
            if c == docId:
                self.tree.Delete(child)
                print "deleted"
                break
            (child, cookie) = self.tree.GetNextChild(self.queryNode, cookie)

    def name_changed(self, docId, name):
        """Remove listing of query document in tree ctrl"""
        print "actually changing name"
        (child, cookie) = self.tree.GetFirstChild(self.queryNode)
        while child.IsOk(): 
            # do something with child
            c = self.tree.GetItemData(child).GetData()
            if c == docId:
                self.tree.SetItemText(child, name)
                break
            (child, cookie) = self.tree.GetNextChild(self.queryNode, cookie)

    def right_click(self, evt):
        pass

    def open_doc(self, evt):
        item = self.tree.GetSelection()
        data = self.tree.GetItemData(item).GetData()
        if data not in ('query', 'report'):
            docType = self.tree.GetItemData(self.tree.GetItemParent(item)).GetData()
            pub.sendMessage('open_document', docType = docType, documentID = data)
            print "open order made", docType, data, "yup"
            

    def add_document(self, name, docId, docType):
        """This handles a new document added message"""
        if docType == 'query':
            parent = self.queryNode
        else:
            parent = self.reportNode
        item = self.tree.AppendItem(parent, name)
        self.tree.SetPyData(item, docId)
