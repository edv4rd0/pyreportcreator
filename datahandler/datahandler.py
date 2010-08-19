# Data layer
from urllib import quote_plus as urlquote
from sqlalchemy import create_engine, MetaData, Column, Table, ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.engine import reflection

xstr = lambda s: s or "" # got this off an aswer to a stackoverflow question. Useful for handling None values

dataConnections = {} #holds all data connections

def CreateDataConnection(database, databaseType, address, user = None, password = None, port = None, relAddress = None):
    """Create connection string then initialize connection object"""
    if user is None:
        if relAddress is None:
            connectionString = databaseType+":////:"+address+database
        if relAddress is True:
            connectionString = databaseType+":///:"+address+database
    if user:
        connectionString = databaseType+"://:"+user+":"+urlquote(xstr(password))+"@"+address+database
    
    dataConnections = (create_engine(connectionString, echo = True)) #create new engine

class DataConnectionsModel(object):
    

    
class DataTable(object):
    """This class holds metadata about each table"""
    def __init__(self, table):
        """Initialize the table model"""

DataConnectionFactory("databasename", "mysql", "localhost", "admin", '')
