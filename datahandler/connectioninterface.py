"""This module deals with setting up specific connection types. It translates between the database specific data and the one big function"""
import datahandler
from pubsub import pub
import string

def establish_sqlite_connection(address, profile):
    """Establish an SQLite connection."""
    
    import sys
    i = ""
    if sys.platform != "win32":
        try:
            i = string.rindex(address, "/")
            print i
            print "\n" 
        except ValueError:
            print ValueError
    else:
        try:
            i = string.rindex(address, "\\")
        except ValueError:
            return ValueError
    name = address[i:]
    address = address[:i+1]
    #check if already connected to database
    dbID = profile.conn_not_exist('sqlite', name, address)
    if dbID != False:
        connID = datahandler.ConnectionManager.create_new_data_connection(u"sqlite", address, name, dbID = dbID)
    else:
        connID = datahandler.ConnectionManager.create_new_data_connection(u"sqlite", address, name)
    if connID != False:
        if datahandler.DataHandler.add(connID):
            pub.sendMessage('dataconnection.save', connID = connID, type = "sqlite", address = address, dbName = name)
            pub.sendMessage('database.added', connID)
            return True                
        else:
            return False
    else:
        return False

#-------------------------------------------------------#

def establish_other_connection(dbType, dbName, serverAddress, serverPort, dbUser, dbPassword, profile):
    """Establish a postgresql or mysql connection."""
    if serverPort == '    ':
        serverPort = None
    dbID = profile.conn_not_exist(dbType, dbName, serverAddress, serverPort, dbUser, dbPassword)
    if dbID != False:
        connID = datahandler.ConnectionManager.create_new_data_connection(databaseType = dbType, address = serverAddress, dbname = dbName, user = dbUser, password = dbPassword, port = serverPort, dbID = dbID)
    else:
        connID = datahandler.ConnectionManager.create_new_data_connection(databaseType = dbType, address = serverAddress, dbname = dbName, user = dbUser, password = dbPassword, port = serverPort)
    if connID != False:
        if datahandler.DataHandler.add(connID):
            pub.sendMessage('dataconnection.save', connID = connID, type = dbType, address = serverAddress, dbName = dbName, username = dbUser, password = dbPassword, port = serverPort)
            pub.sendMessage('databaseadded', connID = connID)
            return True
        else:
            return False
    else:
        return False
