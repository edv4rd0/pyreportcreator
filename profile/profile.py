from sqlalchemy import select


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

class ProfileHandler(object):
    """Handles the storing, loading and saving of profile objects"""
    
    @classmethod
    def init_profile_object(cls):
        """Initialize an empty profile object"""
        try:
            cls.profile = Profile()
            return True
        except:
            return False   
    
    @classmethod
    def save_profile(cls, fileName):
        """Pickles profile to file"""
        import cPickle
        try:
            cls.file = open(fileName, 'w')
            cPickle.dump(cls.profile, cls.file)
            return True
        except PicklingError, e:
            return e
        
    @classmethod
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
        
class Query(object):
    """Defines a query"""

    _name = ""
    queryDefinition = dict() #stores the definition
    engineID = 0
    
    def __init__(self, name = "Untitled"):
        """This initializes the query object from some supplied definitions"""
        self._name = name
        self.queryDefinition['selectItems'] = []

    def change_name(self, newName):
        """Change name of query"""
        self._name = newName
    
    def add_select_item(self, table, column):
        """Add a select item to the query"""
        if (table, column) not in self.selectItems:
            self.selectItems.append((table, column))
            return True
        else:
            return False

    def remove_select_item(self, table, column):
        """Remove a select item from the query"""
        try:
            i = self.queryDefinition['selectItems'].index((table, column))
            self.queryDefinition['selectItems'].remove(i)
            return True
        except IndexError:
            print IndexError
            return False

    def add_condition(self, firstField, secondField, operator):
        """Adds a condition to the query defintion. It will first check if it exists"""
        if firstField is String:
            pass

    def alter_condition(self, condition):
        pass

    def add_join(self):
        """Add a join to the query definition"""
        pass

    def remove_join(self):
        """Remove a join form the definition"""

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

    def build_join_expression(self, joinDefinition):
        """Creates the join expression for the query"""
        pass

    def build_query(self):
        """Builds query by creating all objects based on the unicode 
        string descriptors stored in the query object"""
        query = []
        for t in queryDefinition['selectItems']:
            for c in queryDefinition['selectItems'][t]:
                query.append(metadata.DataObjectHandler.get_column_object(t, cls.queryDefinition['connID'], c))
        return query
