import unittest2 as unittest
import querybuilder
from pyreportcreator.profile import profile, query
import datahandler

class QueryBuilderTest(unittest.TestCase):
    """Test building an SQLAlchemy query from a profile object"""

    def setUp(self):
        self.connID = datahandler.ConnectionManager.create_new_data_connection(databaseType = 'mysql', address = 'localhost', dbname = 'store', user = 'pytest', password = 'P@ssw0rd')
        datahandler.DataHandler.add(self.connID)
        #build simple, basic single table query
        self.queryObjSimple = profile.Query(1, self.connID, "Test Query")
        self.queryObjSimple.add_select_item('tblproduct', 'productID')
        self.queryObjSimple.add_select_item('tblproduct', 'name')
        self.queryObjSimple.add_select_item('tblproduct', 'ISBN')
        self.queryObjSimple.add_select_item('tblproduct', 'price')
        #Single table query with conditions
        self.queryObjConditions = profile.Query(1, self.connID, "Test Query")
        self.queryObjConditions.add_select_item('tblproduct', 'productID')
        self.queryObjConditions.add_select_item('tblproduct', 'name')
        self.queryObjConditions.add_select_item('tblproduct', 'ISBN')
        self.queryObjConditions.add_select_item('tblproduct', 'price')
        ## We will access the objects directly - profile Query object interface not up to it
        query.condition_factory('set', 1, self.queryObjConditions.conditions, None, 'or')
        query.condition_factory('condition', 2, query.find_set(1, self.queryObjConditions.conditions))
        query.condition_factory('condition', 3, query.find_set(1, self.queryObjConditions.conditions))
        query.find_set(1, self.queryObjConditions.conditions).firstObj.configure_condition(('tblproduct', 'price'), 5, '>')
        query.find_set(1, self.queryObjConditions.conditions).firstObj.configure_condition(('tblproduct', 'productID'), 2, '==')
    def test_build_single_table_query(self):
        """
        Test a simple, single table query with no conditions.
        """
        query = querybuilder.build_query(self.queryObjSimple)
        result = datahandler.ConnectionManager.dataConnections[self.connID].execute(query)
        for i in result:
            print i

    def test_build_single_table_with_conditions(self):
        """
        test a simple, single table query with conditions
        """
        print self.queryObjConditions.conditions
        query = querybuilder.build_query(self.queryObjConditions)
        result = datahandler.ConnectionManager.dataConnections[self.connID].execute(query)
        for i in result:
            print i

        

if __name__ == '__main__':
    unittest.main()
