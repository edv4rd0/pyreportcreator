from pubsub import pub #PubSub implements a Publisher - Subscriber pattern for the application
#OK, query object's condition expression consists of conditions which each specify their parent and left sibling (except the leftmost, which is set to Null
# ThisAllows multiple nested sets

class Profile(object):
    """A profile object. This stores query, report and data connection objects"""
    def __init__(self):
        self._fileName = ""
        self.queries = dict() #stores query objects
        self.connections = dict()
        self.reports = []

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

    def save_profile(cls, fileName):
        """Pickles profile to file"""
        import cPickle
        try:
            cls.file = open(fileName, 'w')
            cPickle.dump(cls.profile, cls.file)
            return True
        except PicklingError, e:
            return e
        
    def open_profile(cls, fileName):
        """Opens file and unpickles it"""
        import cPickle
        try:
            cls.file = open(fileName, 'r')
            cls.profile = cPickle.load(cls.file)
            return True
        except UnPicklingError, e:
            returnValues = (e, filename)
            return returnValues
        
    def new_document(self, docType, engineID):
        """Create new document"""
        import uuid
        if docType == 'query':
            documentID = uuid.uuid4()
            while documentID in self.queries.keys():
                documentID = uuid.uuid4()
            self.queries[documentID] = Query(documentID, engineID)
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
        state = self._STATE_ALTERED
        pub.sendMessage('document.state.altered', self._documentID)

    def was_saved(self):
        """This allows items like toolbars to register that it doesn't need saving"""
        state = self.__STATE_SAVED
        pub.sendMessage('document.state.saved', self._documentID)

#-----------------------------------------------------------------#

class Query(Document):
    """Defines a query document"""

    # for concatenating operators
    O_AND = "inclusive"
    O_OR = "inclusive"
    O_NOT = "exclusive"
    #data definition
    distinct = False
    selectItems = dict()
    conditions = dict() #Dict of list of tuples. Each key is a different
    # 'set' of related conditions. Think of there being an OR between each one.
    order_by = tuple() #single tuple of (table, column, direction)
    joins = dict() #firstjoin => join info, secondJoin => join info
    engineID = 0
    

    def __init__(self, documentID, engineID, name = "Untitled Query"):
        """This initializes the query object from some supplied definitions"""
        super(__init__(documentID, name))
        sub.subscribe(add_select_item, 'document.query.select.add')
        sub.subscribe(add_condition, 'document.query.condition.add')
        sub.subscribe(edit_condition, 'document.query.condition.edit')
        sub.subscribe(add_join, 'document.query.join.add')
        

    def change_name(self, newName):
        """Change name of query"""
        self._name = newName
        sub.sendMessage('document.name_change', self._name, self._documentID)
        self.change_made()
    

    def add_select_item(self, table, column):
        """Add a select item to the query. If from a new table, this must
        check how the user wants to join the two tables."""
        if table in self.selectItems.keys():
            if column not in self.selectItems[table]:
                self.selectItems[table].append(column)
                self.change_made()
                pub.sendMessage('query.add_select.success', table, column, self._documentID)
            else:
                pub.sendMessage('query.add_select.duplicate', table, column, self._documentID)
        else:
            self.selectItems[table] = [column]
            self.change_made()
            pub.sendMessage('query.add_select.success', table, column, self._documentID)


    def check_for_dependent_join(self, table):
        """Checks for any dependent joins"""
        for i in self.join.keys():
            if table in i:
                return True
        return False


    def remove_select_item(self, table, column, force = False):
        """Remove a select item from the query.
        This must check to see if removing it would render a join statement useless."""
        if table in self.selectItems.keys():
            if column in self.selectItems and len(self.selectItems) is 1:
                if check_for_dependent_join(table) is True:
                    if f == False:
                        pub.sendMessage('query.del_select.join_exists_error', table, column, self._documentID)
                    else:
                        try:
                            self.selectItems[table].remove(column)
                            self.change_made()
                            pub.sendMessage('query.del_select.success', table, column, self._documentID)
                        except KeyError, IndexError:
                            pub.sendMessage('query.del_select.not_exist', self._documentID)
                else:
                    try:
                        self.selectItems[table].remove(column)
                        self.change_made()
                        pub.sendMessage('query.del_select.success', table, column, self._documentID)
                    except KeyError, IndexError:
                        pub.sendMessage('query.del_select.not_exist', self._documentID)
            try:
                self.selectItems[table].remove(column)
                pub.sendMessage('query.del_select.success', table, column, self._documentID)
                self.change_made()
            except KeyError, IndexError:
                pub.sendMessage('query.del_select.not_exist', self._documentID)
                

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
        """Add a join to the query definition.
        @params: leftTable is the table name of the left, or main table.
                joiningTable is the table being joined onto leftTable.
                type: the type of join chosen 'left' or 'inner'"""
        try:
            if (leftTable, joiningTable) in self.joins.keys():
                self.joins[(leftTable, joiningTable)] = (type, tableValue, joiningValue, opr)
            elif (joiningTable, leftTable) in self.joins.keys():
                self.joins[(leftTable, joiningTable)] = (type, tableValue, joiningValue, opr)
            else:
                self.joins[(leftTable, joiningTable)] = (type, tableValue, joiningValue, opr)
            pub.sendMessage('query.add_join.success', self._documentID, leftTable, joiningTable)
        except:
            pub.sendMessage('query.add_join.failure', self._documentID) 
            
    def remove_join(self, ):
        """Remove a join from the definition"""
        pass
        
    def describe_join(self):
        """Describe the join"""
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

