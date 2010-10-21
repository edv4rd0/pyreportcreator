"""This module deals with setting up specific connection types. It translates between the database specific data and the one big function"""
import datahandler
from pubsub import pub
import string

def establish_sqlite_connection(address):
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
    connID = datahandler.ConnectionManager.CreateNewDataConnection(u"sqlite", address, name)
    if connID != False:
        if datahandler.DataHandler.add(connID):
            pub.sendMessage('dataconnection.save', connID = connID, type = "sqlite", address = address, dbName = name)
            pub.sendMessage('database.added', connID)
            return True                
        else:
            print "fail"
            return False
    else:
        print "connection failed "+ address + " " + name
        return False

#-------------------------------------------------------#

def establish_other_connection(dbType, dbName, serverAddress, serverPort, dbUser, dbPassword):
    """Establish a postgresql or mysql connection."""
    print "Attempting connection\n"
    print ("dbType", "dbName", "serverAddress", "serverPort", "dbuser", "dbPassword"), "\n"
    print (dbType, dbName, serverAddress, serverPort, dbUser, dbPassword)
    
    if serverPort == '    ':
        serverPort = None
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
