import sqlalchemy
from sqlalchemy import MetaData
from sqlalchemy.engine import reflection
from sqlalchemy import Table, Column, String, Integer, ForeignKey
from sqlalchemy import create_engine
from urllib import quote_plus as urlquote

xstr = lambda s: s or ""

class ConnectionManager(object):
    """This class creates the engines and holds all engines in memory."""
    
    dataConnections = dict() #holds all data connections
    
    @classmethod
    def CreateNewDataConnection(cls, databaseType, address, dbname = None, user = None, password = None, port = None, driver = None, dbID = None):
        """Create connection string then initialize connection object"""
        
        if databaseType == u'sqlite':
            if driver:
                #Loads pysqlite2 first if installed, must be able to override this
                connectionString = "sqlite+"+driver+":///"+address+xstr(dbname) #CHECK: relative and absolute paths
            else:
                connectionString = "sqlite:///"+address+xstr(dbname) #CHECK: relative and absolute paths
                
        if databaseType != u'sqlite':
            if user:
                if driver and port:
                    connectionString = databaseType+"+"+driver+"://:"+user+":"+urlquote(xstr(password))+"@"+address+":"+port+"/"+dbname
                elif driver:
                    connectionString = databaseType+"+"+driver+"://:"+user+":"+urlquote(xstr(password))+"@"+address+"/"+dbname
                elif driver == None and port:
                    connectionString = databaseType+"://:"+user+":"+urlquote(xstr(password))+"@"+address+":"+port+"/"+dbname
                else:
                    databaseType+"://"+address+"/"+dbname
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
            cls.dataConnections[dbID] = (create_engine(connectionString, pool_recycle=3600, echo = True)) #create new engine
        else:
            cls.dataConnections[dbID] = (create_engine(connectionString, echo = True)) #create new engine
        #TODO: turn off 'echo = True' before shipping
        try:
            testConnection = cls.dataConnections[dbID].connect()
            testConnection.close()
            print "Success" #TODO: remove this
            return dbID
        except:
            del cls.dataConnections[dbID]
            print "Failure" #TODO Remove this
            return False


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
            #TODO: Actually raise errors (will have to update calling code)

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
        return [(c.name, c.type) for c in cls.metaData[connID].tables[tableName].columns]

    @classmethod
    def get_table_object(cls, tableName, connID):
        """Returns table object based on two supplied identifying strings"""
        table = cls.dataObjects[connID][tableName]
        return table

    @classmethod
    def get_column_object(cls, tableName, connID, colName):
        """Returns column object based on three supplied identifying strings"""
        col = cls.dataObjects[connID][tableName].columns[colName]
        col_type = cls.metaData[connID][tableName].columns[colName].type
        return (col, col_type) #type is returned also, so the GUI can know which controls to use


def destroy_all_freaking_things():
    """This is a scary, undoable, wipe stuff from memory it better be saved - function. Yeah."""
    ConnectionManager.dataConnections = dict()
    DataHandler.metaData = dict()
    DataHandler.dataObjects = dict()
    pub.sendMessage('destroyed.data')