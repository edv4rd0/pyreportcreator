import unittest2 as unittest
import datahandler
from sqlalchemy.engine import reflection

class ConnectionTest(unittest.TestCase):
    """
    test the connection handler class etc
    """
    def setUp(self):
        pass
    def test_connection_to_mysql(self):
        """
        Test that it can make a connection to a test database called 'store' on localhost.
        User is pytest with password P@ssw0rd.
        """
        datahandler.ConnectionManager.create_new_data_connection(databaseType = 'mysql', address = 'localhost', dbname = 'store', user = 'pytest', password = 'P@ssw0rd')

        self.assertEqual(len(datahandler.ConnectionManager.dataConnections.keys()), 1)

class DatahandlerTest(unittest.TestCase):
    """
    Tests the handling of Metadata and Data(table) objects
    """

    def setUp(self):
        """Setup shit"""
        self.connID = datahandler.ConnectionManager.create_new_data_connection(databaseType = 'mysql', address = 'localhost', dbname = 'store', user = 'pytest', password = 'P@ssw0rd')
        self.insp = reflection.Inspector.from_engine(datahandler.ConnectionManager.dataConnections[self.connID])

    def test_return_relations(self):
        relations = datahandler.return_relationship_info(self.connID, 'tblproduct', 'tblinvoicelines')
        self.assertIsInstance(relations, list)

    def test_check_relations(self):
        """
        Check that DataHandler.check_relations() returns a list of dicts defining the relations is it is supposed to.
        Checked on a known good set of tables
        """
        relations = datahandler.DataHandler.check_relations(self.insp, 'tblproduct', 'tblinvoicelines')
        self.assertIsInstance(relations, list)
        self.assertIsInstance(relations[0], dict)
        

if __name__ == '__main__':
    unittest.main()
