# Module which handles establishing and managing data base connections
# Edward Williams edward.pendragon@gmail.com
# 
from urllib import quote_plus as urlquote
from sqlalchemy import create_engine


xstr = lambda s: s or ""

class ConnectionManager(object):
    """This class manages the connections to databases"""
    
    dataConnections = dict() #holds all data connections
    metaData = dict()
    
    @classmethod
    def CreateDataConnection(cls, databaseType, address, dbname = None, user = None, password = None, port = None, driver = None):
        """Create connection string then initialize connection object"""
        if databaseType == u'sqlite':
            if driver:
                #Loads pysqlite2 first if installed, must be able to override this
                connectionString = "sqlite+"+driver+":///"+address #CHECK: relative and absolute paths
            else:    
                connectionString = "sqlite:///"+address #CHECK: relative and absolute paths
                
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
            
        if databaseType == u'mysql':
            cls.dataConnections[dbname] = (create_engine(connectionString, pool_recycle=3600, echo = True)) #create new engine
        else:
            cls.dataConnections[dbname] = (create_engine(connectionString, echo = True)) #create new engine
        #TODO: turn off 'echo = True' before shipping
        try:
            testConnection = cls.dataConnections[dbname].connect()
            testConnection.close()
            print "Success"
        except:
            # log error
            del cls.dataConnections[dbname]
            print "Failure"

ConnectionManager.CreateDataConnection(u'sqlite', u'testdb.db')
