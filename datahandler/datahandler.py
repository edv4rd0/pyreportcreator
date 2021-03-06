import sqlalchemy
from sqlalchemy import MetaData, exc
from sqlalchemy.engine import reflection
from sqlalchemy import Table, Column, String, Integer, ForeignKey
from sqlalchemy import create_engine
from urllib import quote_plus as urlquote

xstr = lambda s: s or ""

def load_data_connections(connections):
    """Load data connections and meta data"""
    for i in connections.keys():
        con = connections[i]
        try:
            ConnectionManager.create_new_data_connection(con[0], con[1], con[2], con[3], con[4], port = con[5], dbID = i)
            DataHandler.add(i)
            DataHandler.add_data_objects(i)
        except sqlalchemy.exc.OperationalError:
            pass

class ConnectionManager(object):
    """This class creates the engines and holds all engines in memory."""
    
    dataConnections = dict() #holds all data connections
    
    @classmethod
    def create_new_data_connection(cls, databaseType, address, dbname = None, user = None, password = None, port = None, driver = None, dbID = None):
        """Create connection string then initialize connection object"""
        connectionString = ""
        if databaseType == u'sqlite':
            if driver:
                #Loads pysqlite2 first if installed, must be able to override this
                connectionString = "sqlite+"+driver+":///"+address+xstr(dbname) #CHECK: relative and absolute paths
            else:
                connectionString = "sqlite:///"+address+xstr(dbname) #CHECK: relative and absolute paths
        else:
            if user:
                if driver and port:
                    connectionString = databaseType+"+"+driver+"://:"+user+":"+urlquote(xstr(password))+"@"+address+":"+port+"/"+dbname
                elif driver:
                    connectionString = databaseType+"+"+driver+"://:"+user+":"+urlquote(xstr(password))+"@"+address+"/"+dbname
                elif driver == None and port:
                    connectionString = databaseType+"://"+user+":"+urlquote(xstr(password))+"@"+address+":"+port+"/"+dbname
                else:
                    connectionString = databaseType+"://"+user+":"+urlquote(xstr(password))+"@"+address+"/"+dbname
            else:
                if driver and port:
                    connectionString = databaseType+"+"+driver+"://:"+address+":"+port+"/"+dbname
                elif driver:
                    connectionString = databaseType+"+"+driver+"://:"+address+"/"+dbname
                elif driver == None and port:
                    connectionString = databaseType+"://:"+address+":"+port+"/"+dbname
                else:
                    connectionString = databaseType+"://:"+address+"/"+dbname

        if dbID == None: 
            dbID = hash(address + "," + xstr(dbname)) #create unique ID
            
        #create engines
        if databaseType == u'mysql':
            cls.dataConnections[dbID] = (create_engine(connectionString, pool_recycle=3600, echo = False)) #create new engine
        else:
            cls.dataConnections[dbID] = (create_engine(connectionString, echo = False)) #create new engine
        try:
            testConnection = cls.dataConnections[dbID].connect()
            testConnection.close()
        except sqlalchemy.exc.OperationalError:
            return False
        return dbID


class DataHandler(object):
    """Stores meta data for databases. The DataObject Handler class interfaces with it to load it's data objects."""
    metaData = dict()
    dataObjects = dict()

    @classmethod
    def add(cls, connID):
        """Add metadata object, auto reflect tables"""
        cls.metaData[connID] = MetaData()
        cls.metaData[connID].reflect(bind=ConnectionManager.dataConnections[connID])
        try:
            cls.add_data_objects(connID)
            return True
        except:
            return False

    @classmethod
    def check_relations(cls, insp, t1, t2):
        """
        Check if there is a relationship between the two columns and return a list of dicts and a boolean if so.
        The boolean specifies whether the relation is a One to One (True) or a One to Many (False)
        @Params:
        t1, t2 are strings of the table names
        """
        relations = []   
        try:
            for i in insp.get_foreign_keys(t1):
                if i['referred_table'] == t2:
                    #check if a one to one relationship (unique constraint)
                    indexes = insp.get_indexes(t2)
                    oneToOne = False
                    for index in indexes:
                        if index['unique'] == True:
                            if i['referred_columns'] in index['column_names']:
                                oneToOne = True
                    #append relationship
                    relations.append({'local_table': t1, 'local_columns': i['constrained_columns'], \
                                      'foreign_table': t2, 'foreign_columns': i['referred_columns'], 'unique': oneToOne})
            for i in insp.get_foreign_keys(t2):
                if i['referred_table'] == t1:
                    indexes = insp.get_indexes(t1)
                    oneToOne = False
                    for index in indexes:
                        if index['unique'] == True:
                            if i['referred_columns'] in index['column_names']:
                                oneToOne = True
                    relations.append({'local_table': t2, 'local_columns': i['constrained_columns'], \
                                      'foreign_table': t1, 'foreign_columns': i['referred_columns'], 'unique': oneToOne})
        except exc.NoSuchTableError:
            return False
        if len(relations) == 1:
            return relations
        elif len(relations) > 1:
            return relations
        else:
            return False

    @classmethod
    def add_data_objects(cls, connID):
        """Build up table objects"""
        cls.dataObjects[connID] = dict()
        for t in cls.get_tables(connID):
            cls.dataObjects[connID][t] = cls.metaData[connID].tables[t]
        
    @classmethod
    def remove(cls, connID):
        """Remove meta data entry"""
        try:
            del cls.metaData[connID]
            return True
        except KeyError:
            return False

    @classmethod
    def refresh_all(cls):
        """Refresh all meta data"""
        for m in cls.metaData.keys():
            cls.metaData[m].reflect(bind=ConnectionManager.dataConnections[m])

    @classmethod
    def get_tables(cls, connID):
        """Return list of table names per db conection"""
        return [t.name for t in cls.metaData[connID].sorted_tables]

    @classmethod
    def get_columns(cls, connID, tableName):
        """Return a list of column names. type is returned also, so the GUI can know which controls to use"""
        return [(c.name, c.type, c.primary_key) for c in cls.metaData[connID].tables[tableName].columns]

    @classmethod
    def get_column_type_object(cls, connID, tableName, colName):
        """Return a single tuple containing data column info"""
        return cls.metaData[connID].tables[tableName].columns[colName].type

    @classmethod
    def get_table_object(cls, tableName, connID):
        """Returns table object based on two supplied identifying strings"""
        table = cls.dataObjects[connID][tableName]
        return table

    @classmethod
    def get_column_object(cls, tableName, connID, colName):
        """Returns column object based on three supplied identifying strings"""
        col = cls.dataObjects[connID][tableName].columns[colName]
        #col_type = cls.metaData[connID][tableName].columns[colName].type
        return col #type is returned also, so the GUI can know which controls to use


def destroy_all_freaking_things():
    """This is a scary, undoable, wipe stuff from memory it better be saved - function. Yeah."""
    ConnectionManager.dataConnections = dict()
    DataHandler.metaData = dict()
    DataHandler.dataObjects = dict()
    pub.sendMessage('destroyed.data')

def return_relationship_info(databaseID, table1, table2):
    """
    Instantiate a schema introspection object and scan for relationships
    @Param:
    database is a sqlalchemy engine object
    
    """
    try:
        insp = reflection.Inspector.from_engine(ConnectionManager.dataConnections[databaseID])
    except KeyError: #database doesn't exist
        print "key error"
        return False
    
    return DataHandler.check_relations(insp, table1, table2)
