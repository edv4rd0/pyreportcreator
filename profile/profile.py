from pyreportcreator.datahandler import metadata
from sqlalchemy import select


class Profile(object):
    """A profile object. This stores query, report and data connection objects"""

    def __init__(self):
        self._fileName = ""
        self.queries = [] #stores query objects

    def save_query(self, query, connAssociated):
        """Save query to dictionary with key being the id for the database connection"""
        self.queries.append((query, connAssociated)) 

    def remove_query(self, queryID):
        """Remove query"""
        pass

    

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
    
    def __init__(self, name, selectItems, whereConditions, joinInfo = None):
        """This initializes the query object from some supplied definitions"""
        self._name = name
        self.queryDefinition['selectItems'] = selectItems
        self.queryDefinition['conditions'] = whereConditions
        if joinInfo:
            self.queryDefinition['joinInfo'] = joinInfo
            
            
    def add_select_item(self, table, column):
        """Add a select item to the query"""
            
    def remove_select_item(self, table, column):
        """Remove a select item from the query"""
        try:
            self.queryDefinition['selectItems'][table].remove[column]
        except ValueError:
            print ValueError

    def describe_join(self):
        """Describe the join"""
        if self.queryDefinition['joinInfo']:
            description = "This is a join to " + str(self.queryDefinition['joinInfo'][0]) + " with the condition: " 
            if self.queryDefinition['joinInfo'][1] == u'=':
                description += str(self.queryDefinition['joinInfo'][2]) + " equal " + str(self.queryDefinition['joinInfo'][3])
            elif self.queryDefinition['joinInfo'][1] == u'like':
                description += str(self.queryDefinition['joinInfo'][2]) + " is like "+ str(self.queryDefinition['joinInfo'][3])
            return description
        else:
            return "There is no join."

    def build_join_expression(self, joinDefinition):
        """Creates the join expression for the query"""
        pass
        #return [firstTable.join(, 
    
    def build_query(self):
        """Builds query by creating all objects based on the unicode 
        string descriptors stored in the query object"""
        query = []
        for t in queryDefinition['selectItems']:
            for c in queryDefinition['selectItems'][t]:
                query.append(metadata.DataObjectHandler.get_column_object(t, cls.queryDefinition['connID'], c))
        return query
        
    def run_query(self):
        """Run the query and return the result"""
        q = build_query() #might need to optimize this later so already built objects just get run
        engine = get_engine() #
        
        return engine.execute(q)
        
ProfileHandler.init_profile_object()
