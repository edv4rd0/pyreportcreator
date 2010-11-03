from pubsub import pub #PubSub implements a Publisher - Subscriber pattern for the application
import query
from pyreportcreator.datahandler import datahandler
import jsonpickle
import zipfile
import shutil
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
            print self.connections[i], [dbType, serverAddress, dbName, dbUser, dbPassword, serverPort]
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
        zf = zipfile.ZipFile(self._fileName, 'a', zipfile.ZIP_DEFLATED)
        print "saving doc", zf.namelist()
        pickled = jsonpickle.encode(self.connections)
        print pickled, "<--pickled"
        info = zipfile.ZipInfo("connections")
        info.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(info, pickled)
        zf.close()
        self.connState = "saved"

    def load_connections(self):
        """Load connections to memory"""
        
        
    def save_profile(self, fileName):
        """Pickles profile to file"""
        self._fileName = fileName
        zf = zipfile.ZipFile(self._fileName, 'w', zipfile.ZIP_DEFLATED)
        for i in self.documents:
            print "saving items"
            pickled = jsonpickle.encode(self.documents[i])
            self.documents[i].was_saved()
            zf.writestr(str(i), pickled)
        pickled = jsonpickle.encode(self.connections)
        zf.writestr('connections', pickled)
        print "saved profile"
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

            

    def open_profile(self, fileName):
        """Opens file and completely erases old objects"""
        self._fileName = fileName
        self.document_index = dict()
        zf = zipfile.ZipFile(self._fileName, 'r', zipfile.ZIP_DEFLATED)
        items = zf.namelist()
        for i in items:
            if str(i) != 'connections':
                doc = self.load_doc_profile(str(i), zf) 
                if isinstance(doc, Query):
                    docType = 'query'
                    print "opening query"
                else:
                    docType = 'report'
                self.document_index[doc.documentID] = docType
                pub.sendMessage('newdocument', name = self.documents[i].name, docId = doc.documentID, docType = docType)
        #load connections
        self.connections = jsonpickle.decode(zf.open(zf.getinfo(docID)).read())
        print "opened profile" 
        zf.close()

    def save_doc(self, document):
        """Save a document to the zip file"""
        zf = zipfile.ZipFile(self._fileName, 'a', zipfile.ZIP_DEFLATED)
        print "saving doc", zf.namelist()
        pickled = jsonpickle.encode(document)
        print pickled, "<--pickled"
        info = zipfile.ZipInfo(document.documentID)
        info.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(info, pickled)
        zf.close()
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
        print "loading", zf.namelist()
        unpickled = jsonpickle.decode(zf.open(zf.getinfo(docID)).read())
        print "unpickled", zf.namelist()
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
        print unpickled.selectItems, "prof:"
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
        self.state = self.__STATE_ALTERED
        pub.sendMessage('document.state.altered', documentID = self.documentID)

    def was_saved(self):
        """This allows items like toolbars to register that it doesn't need saving"""
        self.state = self.__STATE_SAVED
        print self.state
        pub.sendMessage('document.state.saved', documentID = self.documentID)

#-----------------------------------------------------------------#

class Query(Document):
    """Defines a query document"""
    # for concatenating operators
    #data definition
    

    def __init__(self, documentID, engineID, name = "Untitled Query"):
        """This initializes the query object from some supplied definitions"""
        Document.__init__(self, documentID, name)
        self.conditions = query.ConditionSet(0)
        self.counter = 1 #condition id 0 reserved for top condition set
        self.engineID = engineID
        self.distinct = False
        self.selectItems = dict()
        self.group_by = dict() #dict of {'table': 'column'}
        self.order_by = dict() #dict of {'table': ('column', 'direction')}
        self.joins = dict() #firstjoin => join info, secondJoin => join info""
        self.conditionIndex = dict() #for code to check for dependent conditions before deleting select items
        
    def change_name(self, newName):
        """Change name of query"""
        self.name = newName
        pub.sendMessage('document.name_change', name = self.name, documentID = self.documentID)
        self.change_made()

    def check_for_relations(self, table, selTables):
        """
        This runs through the tables already added and checks for relations and returns any mapped relations.
        Need to have the type of relation figured out and returned by the DataHandler module I think.
        """
        relations = []
        if selTables == 1 and len(self.joins.keys()) == 0:
            for t in self.selectItems.keys(): #the keys are table names
                result = datahandler.return_relationship_info(self.engineID, t, table)
                if result != False:
                    joinInfo[(t, table)]
                    pub.sendMessage('query.compose_join', join = joinInfo, documentID = self.documentID)
                else:
                    pub.sendMessage('query.compose_join', documentID = self.documentID)                    
        return relations

    def devise_join(self, localColumns, foreignColumns, localTable, foreignTable):
        """
        This tries to devise a join based on the existing relationship
        """
        if len(foreign_columns) == 1 and len(localColumns) == 1:
            foreignType = get_type(self.engineID, foreignTable, foreignColumns[0])
            localType = get_type(self.engineID, localTable, localColumns[0])        

    def add_select_item(self, table, column):
        """
        Add a select item to the query. If from a new, second table, this must
        check how the user wants to join the two tables.
        """
        print self.documentID, self.selectItems################################################################################
        if table in self.selectItems.keys():
            if column not in [c[0] for c in self.selectItems[table]]:
                self.selectItems[table].append([column, 0])
                #assert(self.selectItems[table].index([column, 0]) == 0)
                self.change_made()
                pub.sendMessage('query.add_select.success', column = (table, column), documentID = self.documentID)
            else:
                pub.sendMessage('query.add_select.duplicate', column = (table, column), documentID = self.documentID)
        else:
            if len(self.selectItems.keys()) == 1:
                check = self.check_for_relations(table, 1)
            self.selectItems[table] = list()
            self.selectItems[table].append([column, 0])
            self.change_made()
            pub.sendMessage('query.add_select.success', column = (table, column), documentID = self.documentID)

    def check_for_dependent_join(self, table):
        """Checks for any dependent joins"""
        for i in self.joins.keys():
            if table in i:
                return True
        return False

    def remove_select_item(self, table, column, force = False):
        """
        Remove a select item from the query.
        This must check to see if removing it would render a join statement useless.
        This must also remove the table entry if there are no longer any columns.
        """
        try:
            if len(self.selectItems[table]) is 1:
                if self.check_for_dependent_join(table) is True:
                    if f == False:
                        #pub.sendMessage('query.del_select.join_exists_error', tbl = table, col = column, documentID = self.documentID)
                        raise JoinException()
                    else:
                        try:
                            del self.selectItems[table] #it's the last column, remove table
                            self.change_made()
                            pub.sendMessage('query.del_select.success', tbl = table, col = column, documentID = self.documentID)
                        except KeyError:
                            pub.sendMessage('query.del_select.not_exist', tbl = table, col = column, documentID = self.documentID)
                else:
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

    def add_join(self, leftTable, joiningTable, type, tableValue, joiningValue, opr):
        """
        Add a join to the query definition.
        @params: leftTable is the table name of the left, or main table.
                joiningTable is the table being joined onto leftTable.
                type: the type of join chosen 'left' or 'inner'
                tableValue: the column or value connected with the left table
                joiningValue: the column or value connected with the jooining table
                opr: the operator ('==', etc)
        """
        try:
            if (leftTable, joiningTable) in self.joins.keys():
                self.joins[(leftTable, joiningTable)] = [type, (leftTable, tableValue), (joiningTable, joiningValue), opr]
            elif (joiningTable, leftTable) in self.joins.keys():
                del self.joins[(joiningTable, leftTable)]
                self.joins[(leftTable, joiningTable)] = [type, (leftTable, tableValue), (joiningTable, joiningValue), opr]
            else:
                self.joins[(leftTable, joiningTable)] = (type, (leftTable, tableValue), (joiningTable, joiningValue), opr)
            pub.sendMessage('query.add_join.success', documentID, self.documentID, join = (leftTable, joiningTable))
            self.change_made()
            return True
        except:
            pub.sendMessage('query.add_join.failure', documentID = self.documentID) 
            return False


    def remove_join(self, table1, table2):
        """
        Remove a join from the definition
        """
        try:
            if (table1, table2) in self.joins.keys():
                del self.joins[(table1, table2)]
                self.change_made()
            elif (table2, table1) in self.joins.keys():
                del self.joins[(table2, table1)]
                self.change_made()
            else:
                return True #nothing changed
            return True
        except:
            pub.sendMessage('query.remove_join.failure', documentID = self.documentID) 
            return False

    def describe_join(self):
        """
        Describe the join
        """
        if self.queryDefinition['joinInfo']:
            description = "This is a join to " + str(self.queryDefinition['joinInfo'][0]) + " with the condition: " 
            if self.queryDefinition['joinInfo'][1] == '=':
                description += str(self.queryDefinition['joinInfo'][2]) + " equal " + str(self.queryDefinition['joinInfo'][3])
            elif self.queryDefinition['joinInfo'][1] == 'like':
                description += str(self.queryDefinition['joinInfo'][2]) + " is like "+ str(self.queryDefinition['joinInfo'][3])
            return description
        else:
            return "There is no join."
        
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
