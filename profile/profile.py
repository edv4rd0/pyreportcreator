from pubsub import pub #PubSub implements a Publisher - Subscriber pattern for the application
import query
from pyreportcreator.datahandler import datahandler
import jsonpickle
import zipfile
import shutil
import os
#OK, query object's condition expression consists of conditions which each specify their parent and left sibling (except the leftmost, which is set to Null
# ThisAllows multiple nested sets

class JoinException(Exception):
    """There's a join"""
    def __init__(self, var = "There's a join"):
        self.var = var

#-----------------------------------------------------

def get_type(connID, table, column):
    """Interfaces with outside module and returns type to caller"""
    type = datahandler.MetaData.return_type(connID, table, column)
    return type

#------------------------------------------------------

class Profile(object):
    """A profile object. This stores query, report and data connection objects"""
    def __init__(self):
        self._fileName = ""
        self.document_index = dict() #stores document id index
        self.connections = dict()
        self.connState = "saved"
        pub.subscribe(self.add_connection, 'dataconnection.save')

    def conn_not_exist(self, dbType, dbName, serverAddress, serverPort = None, dbUser = None, dbPassword = None):
        """Check whether a database connection exists or not"""
        for i in self.connections:
            if self.connections[i] == [dbType, serverAddress, dbName, dbUser, dbPassword, serverPort]:
                return i
        return False
    
    def add_connection(self, connID, type, address, dbName, username = None, password = None, port = None):
        """Add connection to Profile"""
        self.connections[connID] = [type, address, dbName, username, password, port]
        if self._fileName != "":
            self.write_connections_to_file()
        else:
            self.connState = "altered"
    
    def get_name(self, connID):
        """return database name"""
        try:
            name = self.connection[connID][2]
        except:
            raise AttributeError
        return name

    def write_connections_to_file(self):
        """Write the data connections to disk"""
        try:
            zin = zipfile.ZipFile (self._fileName, 'r', zipfile.ZIP_DEFLATED)
            zout = zipfile.ZipFile (self._fileName+"tmp", 'w', zipfile.ZIP_DEFLATED)
            for item in zin.infolist():
                buffer = zin.read(item.filename)
                if (item.filename != 'connections'):
                    zout.writestr(item, buffer)
            pickled = jsonpickle.encode(self.connections)
            info = zipfile.ZipInfo("connections")
            info.compress_type = zipfile.ZIP_DEFLATED
            zout.writestr(info, pickled)
            zout.close()
            zin.close()
            shutil.copyfile(self._fileName+"tmp", self._fileName)
            os.remove(self._fileName+"tmp")
            self.connState = "saved"
        except IOError:
            zout = zipfile.ZipFile (self._fileName, 'w', zipfile.ZIP_DEFLATED)
            pickled = jsonpickle.encode(self.connections)
            info = zipfile.ZipInfo("connections")
            info.compress_type = zipfile.ZIP_DEFLATED
            zout.writestr(info, pickled)
            zout.close()
            self.connState = "saved"


    def load_connections(self):
        """Load connections to memory"""
        zf = zipfile.ZipFile(self._fileName, 'r', zipfile.ZIP_DEFLATED)
        unpickled = jsonpickle.decode(zf.open("connections").read())
        self.connections = unpickled
        zf.close()
        self.connState = "saved"
        
    def save_profile(self, fileName):
        """Pickles profile to file"""
        self._fileName = fileName
        zf = zipfile.ZipFile(self._fileName, 'w', zipfile.ZIP_DEFLATED)
        for i in self.documents:
            pickled = jsonpickle.encode(self.documents[i])
            self.documents[i].was_saved()
            zf.writestr(str(i), pickled)
        pickled = jsonpickle.encode(self.connections)
        zf.writestr('connections', pickled)
        zf.close()

    def copy_and_save(self, newFile, openDocs):
        """
        This method accepts a new filename and dict of open docs
        """
        try:
            shutil.copyfile(self._fileName, newFile)
            self._fileName = newFile
            for i in openDocs:
                self.save_doc(openDocs[i])
        except IOError:
            self._fileName = newFile
        except shutil.Error:
            pass

            

    def open_profile(self):
        """Opens file and completely erases old objects"""
        zf = zipfile.ZipFile(self._fileName, 'r', zipfile.ZIP_DEFLATED)
        items = zf.namelist()
        for i in items:
            if str(i) != 'connections':
                doc = self.load_doc_profile(str(i), zf) 
                if isinstance(doc, Query):
                    docType = 'query'
                else:
                    docType = 'report'
                self.document_index[doc.documentID] = docType
                pub.sendMessage('newdocument', name = doc.name, docId = doc.documentID, docType = docType)
        #load connections
        try:
            self.connections = jsonpickle.decode(zf.open("connections").read())
        except:
            self.connections = dict()
        zf.close()

    def save_doc(self, document):
        """Save a document to the zip file"""
        zin = zipfile.ZipFile(self._fileName, 'r', zipfile.ZIP_DEFLATED)
        zout = zipfile.ZipFile(self._fileName+"tmp", 'w', zipfile.ZIP_DEFLATED)
        for item in zin.infolist():
            buffer = zin.read(item.filename)
            if (item.filename != document.documentID):
                zout.writestr(item, buffer)
        pickled = jsonpickle.encode(document)
        info = zipfile.ZipInfo(document.documentID)
        info.compress_type = zipfile.ZIP_DEFLATED
        zout.writestr(info, pickled)
        zout.close()
        zin.close()
        shutil.copyfile(self._fileName+"tmp", self._fileName)
        os.remove(self._fileName+"tmp")
        document.was_saved()

    def load_doc_profile(self, docID, zf):
        """for use only within load_profile"""
        unpickled = jsonpickle.decode(zf.open(str(docID)).read())
        for i in unpickled.conditions.conditions:
            if i.condID == unpickled.conditions.firstID:
                unpickled.conditions.firstObj = i
                i.parentObj = unpickled.conditions
            for j in unpickled.conditions.conditions:
                if j.condID == i.nextID:
                    j.prevObj == i
                    i.nextObj == j
                elif i.condID == j.nextID:
                    i.prevObj == j
                    j.nextObj == i
        unpickled.was_saved() #otherwise it'll appear altered
        return unpickled

    def load_doc(self, docID):
        """load a document from the zip file"""
        zf = zipfile.ZipFile(self._fileName, 'r')
        unpickled = jsonpickle.decode(zf.open(zf.getinfo(docID)).read())
        for i in unpickled.conditions.conditions:
            if i.condID == unpickled.conditions.firstID:
                unpickled.conditions.firstObj = i
                i.parentObj = unpickled.conditions
            for j in unpickled.conditions.conditions:
                if j.condID == i.nextID:
                    j.prevObj == i
                    i.nextObj == j
                elif i.condID == j.nextID:
                    i.prevObj == j
                    j.nextObj == i
        zf.close()
        unpickled.was_saved() #otherwise will appear altered
        #self.documents[unpickled.documentID] = unpickled
        return unpickled
        
    def new_document(self, docType, engineID = None):
        """Create new document"""
        import uuid
        if docType == 'query':
            documentID = str(uuid.uuid4())
            while documentID in self.document_index:
                documentID = str(uuid.uuid4())
            self.document_index[documentID] = 'query'
            return Query(documentID, engineID)
        else:
            return False #TODO: change to raise unknown doc type error

#-----------------------------------------------------------------#

class Document(object):
    """Abstract document class"""

    
    def __init__(self, documentID):
        self.__STATE_SAVED = 'saved'
        self.__STATE_NEW = 'new'
        self.__STATE_ALTERED = 'altered'
        self.documentID = documentID
        #self.name = ""
        self.state = self.__STATE_NEW

    def change_made(self):
        """This allows items like save buttons on toolbars to realise it now needs to be saved"""
        self.state = self.__STATE_ALTERED
        pub.sendMessage('document.state.altered', documentID = self.documentID)

    def was_saved(self):
        """This allows items like toolbars to register that it doesn't need saving"""
        self.state = self.__STATE_SAVED
        pub.sendMessage('document.state.saved', documentID = self.documentID)

#-----------------------------------------------------------------#

class Query(Document):
    """Defines a query document"""
    # for concatenating operators
    #data definition
    

    def __init__(self, documentID, engineID):
        """This initializes the query object from some supplied definitions"""
        Document.__init__(self, documentID)
        self.conditions = query.ConditionSet(0)
        self.counter = 1 #condition id 0 reserved for top condition set
        self.engineID = engineID
        self.distinct = False
        self.selectItems = dict()
        self.group_by = dict() #dict of {'table': 'column'}
        self.order_by = dict() #dict of {'table': ('column', 'direction')}
        self.joins = []
        self.conditionIndex = dict() #for code to check for dependent conditions before deleting select items
        self.name = "Untitled Query"
        
    def change_name(self, newName):
        """Change name of query"""
        self.name = newName
        pub.sendMessage('document.name_change', name = self.name, documentID = self.documentID)
        self.change_made()

    def check_for_relations(self, table):
        """
        This runs through the tables already added and checks for relations and returns any mapped relations.
        Need to have the type of relation figured out and returned by the DataHandler module.
        Relations are returned as a list of dicts from the datahandler module like so:
        {'local_table': t2, 'local_columns': i['constrained_columns'], \
        'foreign_table': t1, 'foreign_columns': i['referred_columns'], 'unique': True|False})
        Only two tables allowed per query, so this operates with that assumption.
        """
        for t in self.selectItems.keys(): #the keys are table names
            result = datahandler.return_relationship_info(self.engineID, t, table)
            if result != False:
                result = result[0] #only taking the first relation
                for i in result['local_columns']:
                    leftColType = str(datahandler.DataHandler.get_column_type_object(self.engineID, result['local_table'], i))
                    for j in result['foreign_columns']:
                        if str(datahandler.DataHandler.get_column_type_object(self.engineID, result['foreign_table'], i)) \
                           == leftColType:
                            relation = ((result['local_table'], i), (result['foreign_table'], j))
                            return relation
        return False


    def add_select_item(self, table, column):
        """
        Add a select item to the query. If from a new, second table, this must
        check how the user wants to join the two tables.
        """
        if table in self.selectItems.keys():
            if column not in [c[0] for c in self.selectItems[table]]:
                self.selectItems[table].append([column, 0])
                self.change_made()
                pub.sendMessage('query.add_select.success', column = (table, column), documentID = self.documentID)
            else:
                pub.sendMessage('query.add_select.duplicate', column = (table, column), documentID = self.documentID)
        else:
            if len(self.selectItems.keys()) == 1:
                relation = self.check_for_relations(table)
                if relation != False:
                    #add join based on relationship
                    self.add_join(relation[0][0], relation[1][0], 'inner', relation[0][1], relation[1][1], '==')
                    pub.sendMessage('joinadded', documentID = self.documentID) 
            self.selectItems[table] = list()
            self.selectItems[table].append([column, 0])
            self.change_made()
            pub.sendMessage('query.add_select.success', column = (table, column), documentID = self.documentID)

    def remove_select_item(self, table, column, force = False):
        """
        Remove a select item from the query.
        This must check to see if removing it would render a join statement useless.
        This must also remove the table entry if there are no longer any columns.
        """
        try:
            if len(self.selectItems[table]) is 1:
                try:
                    del self.selectItems[table]
                    self.change_made()
                    pub.sendMessage('query.del_select.success', tbl = table, col = column, documentID = self.documentID)
                except KeyError, IndexError:
                    pub.sendMessage('query.del_select.not_exist', tbl = table, col = column, documentID = self.documentID)
            elif len(self.selectItems[table]) > 1:
                try:
                    for i in self.selectItems[table]:
                        if i in self.selectItems[table]:
                            if i[0] == column:
                                index = self.selectItems[table].index(i)
                                self.selectItems[table].pop(index)
                                pub.sendMessage('query.del_select.success', tbl = table, col = column, documentID = self.documentID)
                                self.change_made()
                except IndexError:
                    pub.sendMessage('query.del_select.not_exist', tbl = table, col = column, documentID = self.documentID)
        except KeyError:
            pub.sendMessage('query.del_select.not_exist', tbl = table, col = column, documentID = self.documentID)
            return None

    def add_condition(self, parent = None, prev = None):
        """
        Adds a condition to the query definition. It will first check if it exists
        """
        self.counter
        if parent == None:
            #top level condition, parentID == 0
            cond = query.condition_factory('condition', self.counter, self.conditions, prev)
            self.counter += 1
            return cond
        else:
            cond = query.condition_factory('condition', self.counter, parent, prev)
            self.counter += 1
            return cond

    def add_set(self, parent = None, prev = None):
        """
        Adds a set to the query definition.
        """
        self.counter
        if parent == None:
            #top level set, parentID == 0
            cond = query.condition_factory('set', self.counter, self.conditions, prev)
            self.counter += 1
            return cond
        else:
            cond = query.condition_factory('set', self.counter, parent, prev)
            self.counter += 1
            return cond

    def remove_condition(self, condition):
        """Removes condition from query definition"""
        condition.remove_self()

    def add_join(self, leftTable, joiningTable, type, tableValue, joiningValue, opr, fakeRight = False):
        """
        Add a join to the query definition.
        @params: leftTable is the table name of the left, or main table.
                joiningTable is the table being joined onto leftTable.
                type: the type of join chosen 'left' or 'inner'
                tableValue: the column or value connected with the left table
                joiningValue: the column or value connected with the jooining table
                opr: the operator ('==', etc)
        """
        if fakeRight:
            self.joins = [type, (joiningTable, joiningValue), (leftTable, tableValue), opr, fakeRight]
        else:
            self.joins = [type, (leftTable, tableValue), (joiningTable, joiningValue), opr, fakeRight]
        self.change_made()
        return True

    def group(self, table, column):
        """Set up GROUP BY on a particular column"""
        try:
            for c in self.selectItems[table]:
                if c[0] == column:
                    c[1] = 1
                    pub.sendMessage('query.group_by.updated', group = (table, column), documentID = self.documentID)
                    self.change_made()
        except KeyError:
            return False
#-----------------------------------------------------------------#

class Report(Document):
    """
    This is a class defining the report document.
    This is the data definition for storing what goes in the report.
    """
    __STATE_SAVED = 'saved'
    __STATE_NEW = 'new'
    __STATE_ALTERED = 'altered'
    state = __STATE_NEW
    name = ""
    documentID = 0
    
    
    def __init__(self, documentID, name = ""):
        self.documentID = documentID
        self.name = name

    def change_made(self):
        """This allows items like save buttons on toolbars to realise it now needs to be saved"""
        state = self._STATE_ALTERED
        pub.sendMessage('document.state.altered', self.documentID)

    def was_saved(self):
        """This allows items like toolbars to register that it doesn't need saving"""
        state = self.__STATE_SAVED
        pub.sendMessage('document.state.saved', self.documentID)

#-----------------------------------------------------------------#
