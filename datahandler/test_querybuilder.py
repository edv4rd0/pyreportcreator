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
        #query.condition_factory('set', 1, self.queryObjConditions.conditions, None, 'or')
        self.queryObjConditions.conditions.boolVal = 'or'
        query.condition_factory('condition', 2, self.queryObjConditions.conditions)
        query.condition_factory('condition', 3, self.queryObjConditions.conditions)
        self.queryObjConditions.conditions.firstObj.configure_condition(('tblproduct', 'price'), 13, '>')
        self.queryObjConditions.conditions.firstObj.nextObj.configure_condition(('tblproduct', 'productID'), 5L, '==')

        #Single table query with nested conditions
        self.queryObjNested = profile.Query(1, self.connID, "Test Query")
        self.queryObjNested.add_select_item('tblproduct', 'productID')
        self.queryObjNested.add_select_item('tblproduct', 'name')
        self.queryObjNested.add_select_item('tblproduct', 'ISBN')
        self.queryObjNested.add_select_item('tblproduct', 'price')
        ## We will access the objects directly - profile Query object interface not up to it
        #query.condition_factory('set', 1, self.queryObjConditions.conditions, None, 'or')
        self.queryObjNested.conditions.boolVal = 'and'
        
        query.condition_factory('set', 1, self.queryObjNested.conditions, None, 'or')
        query.condition_factory('set', 2, self.queryObjNested.conditions, None, 'or')
        
        query.condition_factory('condition', 3, self.queryObjNested.conditions.firstObj)
        query.condition_factory('condition', 4, self.queryObjNested.conditions.firstObj)
        query.condition_factory('condition', 5, self.queryObjNested.conditions.firstObj.nextObj)
        query.condition_factory('condition', 6, self.queryObjNested.conditions.firstObj.nextObj)
        self.queryObjNested.conditions.firstObj.firstObj.configure_condition(('tblproduct', 'price'), 13, '>')
        self.queryObjNested.conditions.firstObj.firstObj.nextObj.configure_condition(('tblproduct', 'productID'), 5L, '==')
        self.queryObjNested.conditions.firstObj.nextObj.firstObj.configure_condition(('tblproduct', 'price'), 13, '>')
        self.queryObjNested.conditions.firstObj.nextObj.firstObj.nextObj.configure_condition(('tblproduct', 'productID'), 5L, '==')
        #join
        self.queryObjNested.add_join('tblproduct', 'tblavailability', 'inner', 'availability', 'id', '==')
    def test_build_single_table_query(self):
        """
        Test a simple, single table query with no conditions.
        """
        query = querybuilder.build_query(self.queryObjSimple)
        result = datahandler.ConnectionManager.dataConnections[self.connID].execute(query)
        for i in result:
            print i

    def test_get_condition(self):
        """
        test the condition builder
        """
        print self.queryObjConditions.conditions.firstObj.nextObj.field1
        querybuilder.get_condition(self.queryObjConditions.conditions.firstObj, self.connID)

    def test_build_single_table_with_conditions(self):
        """
        test a simple, single table query with conditions
        """
        print self.queryObjConditions.conditions
        #print self.queryObjConditions.conditions.firstObj.nextObj.operator
        query2 = querybuilder.build_query(self.queryObjConditions)
        result = datahandler.ConnectionManager.dataConnections[self.connID].execute(query2)
        for i in result:
            print i

    def test_build_single_table_with_nested_conditions(self):
        """
        test a simple, single table query with nested conditions. Yes, very silly query but oh well.
        """
        #print self.queryObjConditions.conditions.firstObj.nextObj.operator
        query2 = querybuilder.build_query(self.queryObjNested)
        result = datahandler.ConnectionManager.dataConnections[self.connID].execute(query2)
        for i in result:
            print i

        

if __name__ == '__main__':
    unittest.main()
