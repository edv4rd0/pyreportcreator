import sqlalchemy
from sqlalchemy import MetaData
from sqlalchemy.engine import reflection
from sqlalchemy import Table, Column, String, Integer, ForeignKey
from sqlalchemy import *
from pyreportcreator.datahandler import connectionmanager

class MetaDataHandler(object):
    """Stores meta data for databases"""
    metaData = dict()
    
    @classmethod
    def add(cls, connID):
        """Add metadata object, auto reflect tables"""
        cls.metaData[connID] = MetaData()
        cls.metaData[connID].reflect(bind=connectionmanager.ConnectionManager.dataConnections[connID])
    
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
            #TODO: get this working, can't be bothered
            cls.metaData[m].reflect(bind=connectionmanager.ConnectionManager.dataConnections[m])
    
    @classmethod
    def get_db_names(cls, connID):
        """Return a list of database connection id's"""
        return [split(i)[2] for i in cls.metaData.keys()]

    @classmethod
    def get_tables(cls, connID):
        """Return list of table names per db conection"""
        
        return [t.name for t in cls.metaData[connID].sorted_tables]
    @classmethod
    def get_columns(cls, connID, tableName):
        """Return a list of column names"""
        return [c.name for c in cls.metaData[connID].tables[tableName].columns]
            
class DataObjectHandler(object):
    """Handles table and column objects"""
    
    tableObjects = dict()
    
    @classmethod
    def get_table_object(cls, tableName, connID):
        """Returns table object based on two supplied identifying strings"""
        table = cls.tableObjects[connID][tableName]
        return table

    @classmethod
    def get_column_object(cls, tableName, connID, colName):
        """Returns column object based on three supplied identifying strings"""
        col = cls.tableObjects[connID][tableName].columns[colName]
        print col
