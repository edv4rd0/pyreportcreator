import unittest2 as unittest
import querybuilder
from pyreportcreator.profile import profile, query
import datahandler

class QueryBuilderTest(unittest.TestCase):
    """Test building an SQLAlchemy query from a profile object"""

    def setUp(self):
        self.connID = datahandler.ConnectionManager.add_new_data_connection(databaseType = 'mysql', address = 'localhost', dbname = 'store', user = 'pytest', password = 'P@ssw0rd')
        #build simple, basic single table query
        self.queryObjSimple = profile.Query(1, self.connID, "Test Query")
        self.queryObjSimple.add_select_item('tblproduct', 'productID')
        self.queryObjSimple.add_select_item('tblproduct', 'name')
        self.queryObjSimple.add_select_item('tblproduct', 'ISBN')
        self.queryObjSimple.add_select_item('tblproduct', 'price')

    def test_build_single_table_query(self):
        """
        Test a simple, single table query with no conditions.
        """
        query = querybuilder.build_query(self.queryObjSimple)
        #self.assertIsInstance(query__str__(), sqlalchemy

if __name__ == '__main__':
    unittest.main()
