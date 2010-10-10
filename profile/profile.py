from pubsub import pub #PubSub implements a Publisher - Subscriber pattern for the application
import query
from pyreportcreator.datahandler import datahandler
#OK, query object's condition expression consists of conditions which each specify their parent and left sibling (except the leftmost, which is set to Null
# ThisAllows multiple nested sets

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
        self.queries = dict() #stores query objects
        self.connections = dict()
        self.reports = dict()

    def save_query(self, query, queryID):
        """Save query to dictionary with key being the id for the database connection"""
        self.queries[queryID] = query

    def remove_query(self, queryID):
        """Remove query"""
        try:
            del self.queries[queryID]
            return True
        except IndexError:
            return False

    def run_query(self, queryID):
        """Run the query and return the result"""
        q = self.queries[queryID].build_query() #might need to optimize this later so already built objects just get run
        engine = datahandler.ConnectionManager.dataConnections[self.queries[queryID].engineID]
        return engine.execute(q)

    def save_connection(self, connID, address, databaseName, user = None, password = None, port = None, driver = None):
        """Save the database connection"""
        try:
            self.connections[connID] = (address, databaseName, user, password, port, driver)
            return True
        except:
            return False

    def save_profile(self, fileName):
        """Pickles profile to file"""
        import cPickle
        try:
            daFile = open(fileName, 'w')
            cPickle.dump(self, daFile)
            return True
        except PicklingError, e:
            return e
        
    def open_profile(self, fileName):
        """Opens file and unpickles it"""
        import cPickle
        try:
            dafile = open(fileName, 'r')
            self = cPickle.load(dafile)
            return True
        except UnPicklingError, e:
            returnValues = (e, filename)
            return returnValues
        
    def new_document(self, docType, engineID = None):
        """Create new document"""
        import uuid
        if docType == 'query':
            documentID = uuid.uuid4()
            while documentID in self.queries.keys():
                documentID = uuid.uuid4()
            self.queries[documentID] = Query(documentID, engineID)
        elif docType == 'report':
            documentID = uuid.uuid4()
            while documentID in self.reports.keys():
                documentID = uuid.uuid4()
            self.reports[documentID] = Report(documentID)
        else:
            return False #TODO: change to raise unknown doc type error

#-----------------------------------------------------------------#

class Document(object):
    """Abstract document class"""
    __STATE_SAVED = 'saved'
    __STATE_NEW = 'new'
    __STATE_ALTERED = 'altered'
    state = __STATE_NEW
    _name = ""
    _documentID = 0
    def __init__(self, documentID, name = ""):
        self._documentID = documentID
        self._name = name

    def change_made(self):
        """This allows items like save buttons on toolbars to realise it now needs to be saved"""
        self.state = self.__STATE_ALTERED
        pub.sendMessage('document.state.altered', documentID = self._documentID)

    def was_saved(self):
        """This allows items like toolbars to register that it doesn't need saving"""
        self.state = self.__STATE_SAVED
        pub.sendMessage('document.state.saved', documentID = self._documentID)

#-----------------------------------------------------------------#

class Query(Document):
    """Defines a query document"""
    # for concatenating operators
    #data definition
    distinct = False
    selectItems = dict()
    counter = None
    conditions = None
    group_by = dict() #dict of {'table': 'column'}
    order_by = dict() #dict of {'table': ('column', 'direction')}
    joins = dict() #firstjoin => join info, secondJoin => join info
    engineID = 0
    

    def __init__(self, documentID, engineID, name = "Untitled Query"):
        """This initializes the query object from some supplied definitions"""
        super(Query, self).__init__(documentID, name)
        self.conditions = query.ConditionSet(0)
        self.counter = 1 #condition id 0 reserved for top condition set

    def change_name(self, newName):
        """Change name of query"""
        self._name = newName
        pub.sendMessage('document.name_change', name = self._name, documentID = self._documentID)
        self.change_made()

    def check_for_relations(self, table, selTables):
        """
        This runs through the tables already added and checks for relations and returns any mapped relations.
        Need to have the type of relation fgured out and returned by the DataHandler module I think.
        """
        relations = []
        if selTables == 1 and len(self.joins.keys()) == 0:
            for t in self.selectItems.keys(): #the keys are table names
                result = datahandler.return_relationship_info(self.engineID, t, table)
                if result != False:
                    joinInfo[(t, table)]
                    pub.sendMessage('query.compose_join', join = joinInfo, documentiD = self._documentID)
                else:
                    pub.sendMessage('query.compose_join', documentID = self._documentID)
                    
        return relations

    def devise_join(self, localColumns, foreignColumns, localTable, foreignTable):
        """
        This is where we get clever and try and devise a join
        """
        if len(foreign_columns) == 1 and len(localColumns) == 1:
            foreignType = get_type(self.engineID, foreignTable, foreignColumns[0])
            localType = get_type(self.engineID, localTable, localColumns[0])
            

    def add_select_item(self, table, column):
        """
        Add a select item to the query. If from a new, second table, this must
        check how the user wants to join the two tables.
        """
        if table in self.selectItems.keys():
            if column not in self.selectItems[table]:
                self.selectItems[table].append(column)
                self.change_made()
                pub.sendMessage('query.add_select.success', column = (table, column), documentID = self._documentID)
            else:
                pub.sendMessage('query.add_select.duplicate', column = (table, column), documentID = self._documentID)
        else:
            if len(self.selectItems.keys()) == 1:
                check = self.check_for_relations(table, 1)
            self.selectItems[table] = list()
            self.selectItems[table].append(column)
            self.change_made()
            pub.sendMessage('query.add_select.success', column = (table, column), documentID = self._documentID)

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
                        pub.sendMessage('query.del_select.join_exists_error', tbl = table, col = column, documentID = self._documentID)
                    else:
                        try:
                            del self.selectItems[table] #it's the last column, remove table
                            self.change_made()
                            pub.sendMessage('query.del_select.success', tbl = table, col = column, documentID = self._documentID)
                        except KeyError:
                            pub.sendMessage('query.del_select.not_exist', tbl = table, col = column, documentID = self._documentID)
                else:
                    try:
                        del self.selectItems[table]
                        self.change_made()
                        pub.sendMessage('query.del_select.success', tbl = table, col = column, documentID = self._documentID)
                    except KeyError, IndexError:
                        pub.sendMessage('query.del_select.not_exist', tbl = table, col = column, documentID = self._documentID)
            elif len(self.selectItems[table]) > 1:
                try:
                    self.selectItems[table].remove(column)
                    pub.sendMessage('query.del_select.success', tbl = table, col = column, documentID = self._documentID)
                    self.change_made()
                except IndexError:
                    pub.sendMessage('query.del_select.not_exist', tbl = table, col = column, documentID = self._documentID)
        except KeyError:
            pub.sendMessage('query.del_select.not_exist', tbl = table, col = column, documentID = self._documentID)
            return
        
    def configure_condition(self, column, operator, valueOrColumn, conditionNo, type):
        """Adds a condition to the query definition. It will first check if it exists"""
        try:
            if self.conditions[conditionNo]:
                for j in self.conditions[conditionNo]:
                    if column == j[0]:
                        i = self.conditions[conditionNo].index(j)
                        if con_type == 'daterange':
                            pass #condition = self.daterange_condition()
                        self.conditions[conditionNo][i]
                        pub.sendMessage('query.condition.added', self._documentID, conditionNo, column)
                        break
        except KeyError:
            self.conditions[conditionNo] = [(column, type, )]
            pub.sendMessage('query.condition.added', self._documentID, conditionNo, column)       
        

    def remove_condition(self, conditionNo, column):
        """Removes condition from query definition"""
        try:
            if len(self.conditions[conditionNo]) == 1:
                self.conditions.remove(self.conditions[conditionNo])
                pub.sendMessage('query.condition.completely_removed', self._documentID)
            else:
                for j in self.conditions[conditionNo]:
                    if column == j[0]:
                        self.conditions[conditionNo].remove(j)
                        break
                pub.sendMessage('query.condition.removed', self._documentID, conditionNo, column)
        except IndexError:
            pub.sendMessage('query.condition.completely_removed', self._documentID)


    def add_join(self, leftTable, joiningTable, type, tableValue, joiningValue, opr):
        """
        Add a join to the query definition.
        @params: leftTable is the table name of the left, or main table.
                joiningTable is the table being joined onto leftTable.
                type: the type of join chosen 'left' or 'inner'
        """
        try:
            if (leftTable, joiningTable) in self.joins.keys():
                self.joins[(leftTable, joiningTable)] = (type, tableValue, joiningValue, opr)
            elif (joiningTable, leftTable) in self.joins.keys():
                del self.joins[(joiningTable, leftTable)]
                self.joins[(leftTable, joiningTable)] = (type, tableValue, joiningValue, opr)
            else:
                self.joins[(leftTable, joiningTable)] = (type, tableValue, joiningValue, opr)
            pub.sendMessage('query.add_join.success', self._documentID, leftTable, joiningTable)
            return True
        except:
            pub.sendMessage('query.add_join.failure', self._documentID) 
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
            pub.sendMessage('query.add_join.failure', self._documentID) 
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
        
    def group(self, column, table):
        """Set up GROUP BY on a particular column"""
        try:
            self.group_by = self.selectValues[table][column]
            pub.sendMessage('query.group_by.updated', table, column, self._documentID)
        except KeyError, IndexError:
            pub.sendMessage('query.group_by.unchanged', self._documentID)

#-----------------------------------------------------------------#

class Report(Document):
    """Abstract document class"""
    __STATE_SAVED = 'saved'
    __STATE_NEW = 'new'
    __STATE_ALTERED = 'altered'
    state = __STATE_NEW
    _name = ""
    _documentID = 0
    def __init__(self, documentID, name = ""):
        self._documentID = documentID
        self._name = name

    def change_made(self):
        """This allows items like save buttons on toolbars to realise it now needs to be saved"""
        state = self._STATE_ALTERED
        pub.sendMessage('document.state.altered', self._documentID)

    def was_saved(self):
        """This allows items like toolbars to register that it doesn't need saving"""
        state = self.__STATE_SAVED
        pub.sendMessage('document.state.saved', self._documentID)

#-----------------------------------------------------------------#
