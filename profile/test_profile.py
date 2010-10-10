import unittest2 as unittest
import profile
from pubsub import pub
import query

class TestProfileMethods(unittest.TestCase):

    def setUp(self):
        self.profileObj = profile.Profile()

    def test_profile_initialization(self):
        """
        Test that the profile class can be initialized
        """
        profileObj = profile.Profile()
        self.assertIsInstance(profileObj, profile.Profile)

    def test_new_query_document(self):
        """
        Test the new_document mehtod that it actually creates a query document and sets the id correctly.
        """
        self.profileObj.new_document(docType = 'query', engineID = 1)
        for i in self.profileObj.queries.keys():
            self.assertIsInstance(self.profileObj.queries[i], profile.Query)
            self.assertEqual(i, self.profileObj.queries[i]._documentID)

    def test_new_report_document(self):
        """
        Test the new_document method that it actually creates a report document and sets the id correctly.
        """
        self.profileObj.new_document(docType = 'report')
        for i in self.profileObj.reports.keys():
            self.assertIsInstance(self.profileObj.reports[i], profile.Report)
            self.assertEqual(i, self.profileObj.reports[i]._documentID)

    def test_saving(self):
        """
        Test profile can pickle it'self
        """
        ret = self.profileObj.save_profile('testsavefile.pro')
        self.assertTrue(ret)

    def test_saving_and_loading(self):
        """
        Test whether a pickled object is restored correctly
        """
        #load a document for testing
        self.profileObj.new_document(docType = 'report')
        for i in self.profileObj.reports.keys():
            self.assertIsInstance(self.profileObj.reports[i], profile.Report)
            self.assertEqual(i, self.profileObj.reports[i]._documentID)
        #save profile object
        ret = self.profileObj.save_profile('testsavefile.pro')
        self.assertTrue(ret)
        #reset project object
        self.profileObj = None
        self.profileObj = profile.Profile()
        #check it's reset
        self.assertEqual(len(self.profileObj.reports), 0)
        #now load file
        ret = self.profileObj.open_profile('testsavefile.pro')
        self.assertTrue(ret)
        #check it actually has the document
        for i in self.profileObj.reports.keys():
            self.assertIsInstance(self.profileObj.reports[i], profile.Report)
                       
        

class TestQueryObject(unittest.TestCase):
    """
    Test the query class
    """

    def dummy_sub_item_del_fail(self, tbl, col, documentID):
        self.assertTrue(tbl)
        self.assertTrue(col)
        self.assertTrue(documentID)
        self.handled = True

    def dummy_sub_item_del_win(self, tbl, col, documentID):
        self.assertTrue(tbl)
        self.assertTrue(col)
        self.assertTrue(documentID)
        self.handled = True

    def dummy_sub_handler(self, name, documentID):
        self.assertTrue(name)
        self.assertTrue(documentID)
        self.handled = True

    def setUp(self):
        pub.subscribe(self.dummy_sub_handler, 'document.name_change')
        pub.subscribe(self.dummy_sub_item_del_fail, 'query.del_select.not_exist')
        pub.subscribe(self.dummy_sub_item_del_win, 'query.del_select.success')
        self.testObj = profile.Query(1,1)
        self.handled = False
        #self.assertEqual(len(self.testObj.selectItems.keys()), 0)

    def tearDown(self):
        unittest.TestCase.setUp(self)
        self.testObj = None

    def test_query_initialization(self):
        """
        test if the query object initializes
        """
        testObj = profile.Query(1,1)
        self.assertIsInstance(testObj, profile.Query)
        self.assertIsInstance(testObj.conditions, query.ConditionSet) #test it's properly setup in __init__
        
    def test_change_name(self):
        """
        test that name is changed, pub sent and name change was handled
        """
        self.testObj.change_name("new name")
        self.assertEqual(self.testObj._name, "new name")
        self.assertTrue(self.handled)

    def test_add_select_item(self):
        """
        Tets whether select items can be added
        """
        self.testObj.add_select_item('tablename', 'columnname')
        print "first",self.testObj.selectItems
        self.assertTrue(self.testObj.selectItems['tablename'])
        self.assertEqual(self.testObj.selectItems['tablename'].index('columnname'), 0)

    def test_add_duplicate_select_item(self):
        """
        Check that duplicate select items being added are handled nicely and data is not screwed up
        """
        self.assertTrue(self.testObj.selectItems['tablename'])
        self.testObj.add_select_item('tablename', 'columnname')
        print "dup",self.testObj.selectItems
        self.assertTrue(self.testObj.selectItems['tablename'])
        self.assertEqual(len(self.testObj.selectItems['tablename']), 1)

    def test_add_column_from_second_table(self):
        """
        Check that adding a second table to the mix is handled correctly
        """
        self.testObj.add_select_item('tablename', 'columnname')
        self.testObj.add_select_item('secondtable', 'columnname')
        print "2ndTable",self.testObj.selectItems
        #join config must be handled
        
        self.assertEqual(len(self.testObj.selectItems.keys()), 2)

    def test_remove_last_select_item(self):
        """
        Test removing the last select item
        """
        self.assertTrue(self.testObj.selectItems['tablename'])
        self.assertEqual(len(self.testObj.selectItems.keys()), 2)
        #OK, now remove it
        self.testObj.remove_select_item('tablename', 'columnname')
        self.assertError(self.testObj.selectItems['tablename'])
        
        
    def test_remove_select_item_not_exist_table(self):
        """
        Test removing an item where table doesn't exist
        """

    def test_remove_select_item_not_exist_column(self):
        """
        Test removing an item where the table actually exists but the column doesn't.
        """
    def test_add_first_condition(self):
        """
        Test whether a simple condition can be added to the condition set
        """
        startCounterValue = self.testObj.counter
        self.assertEqual(self.testObj.conditions.firstObj, None)


if __name__ == '__main__':
    unittest.main()
