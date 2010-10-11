import unittest2 as unittest
import query
from pyreportcreator.datahandler import datahandler

class ConditionTest(unittest.TestCase):
    """
    Test the Condition Object.
    """
    def setUp(self):
        """Test case setup"""
        self.testDBID = datahandler.ConnectionManager.create_new_data_connection('sqlite','/home/edward/src/sqlalchemytest/tutorial.db')
        self.conditionset = query.ConditionSet(0)
        self.counter = 1

    def test_add_condition_to_conditionset(self):
        """
        Test whether a simple condition can be added to the condition set
        """
        query.condition_factory('condition', self.conditionset, self.counter)
        self.assertTrue(self.conditionset[0])

    def test_firstID_is_set(self):
        """
        Test whether the conditionset updates it's pointer to the first condition in the conditionset
        """
        query.condition_factory('condition', self.conditionset, self.counter)
        print self.conditionset
        self.assertEqual(self.conditionset.firstID, self.conditionset[0].condID)
        self.assertNotEqual(self.conditionset.firstObj, None)

    def test_prev_next_continuity_on_add(self):
        """
        Test whether upon adding a second condition to a condition set the prev and next IDs get updated
        and the firstID gets changed. The condition's place is not set in this test. (defaults to first)
        """
        print self.conditionset
        query.condition_factory('condition', self.conditionset, self.counter)
        self.assertEqual(self.conditionset.firstID, self.conditionset[0].condID)
        self.counter +=1
        query.condition_factory('condition', self.conditionset, self.counter)
        print self.conditionset
        self.assertEqual(self.conditionset.firstID, self.conditionset[1].condID)
        #one added second should be first (rule: prev == None, they are first
        self.assertEqual(self.conditionset[0].prevID, self.conditionset[1].condID)
        self.assertEqual(self.conditionset[1].nextID, self.conditionset[0].condID)
        print self.conditionset

    def test_prev_next_continuity_add_child_member(self):
        """
        Test whether upon adding a second condition to a condition set the prev and next IDs get updated
        and the firstID gets changed. The condition's place is set in this test.

        THIS TESTS THE add_child_member() METHOD DIRECTLY
        """
        self.conditionset.add_child_member(query.Condition(self.counter, self.conditionset))
        self.counter +=1
        self.conditionset.add_child_member(query.Condition(self.counter, self.conditionset, self.conditionset.firstObj))
        self.assertEqual(self.conditionset.firstID, self.conditionset[0].condID)
        self.assertEqual(self.conditionset[1].prevID, self.conditionset[0].condID)
        self.assertEqual(self.conditionset[0].nextID, self.conditionset[1].condID)

    def test_prev_next_continuity_on_add_with_place(self):
        """
        Test whether upon adding a second condition to a condition set the prev and next IDs get updated
        and the firstID gets changed. The condition's place is set in this test.
        """
        query.condition_factory('condition', self.conditionset, self.counter)
        self.counter +=1
        query.condition_factory('condition', self.conditionset, self.counter, self.conditionset.firstObj)
        self.assertEqual(self.conditionset.firstID, self.conditionset[0].condID)
        self.assertEqual(self.conditionset[1].prevID, self.conditionset[0].condID)
        self.assertEqual(self.conditionset[0].nextID, self.conditionset[1].condID)

    def test_remove_works(self):
        """
        This test simply tests that the remove method does remove the child
        """
        query.condition_factory('condition', self.conditionset, self.counter)
        self.counter +=1
        query.condition_factory('condition', self.conditionset, self.counter)
        #check index exists
        self.assertTrue(self.conditionset[1])
        #remove
        result = self.conditionset.remove_child(self.counter)
        self.assertEqual(result, True)
        #check it's gone
        with self.assertRaises(IndexError):
            self.conditionset[1]

    def test_prev_next_continuity_on_remove(self):
        """
        Test whether upon deleteing a child the pointers to prev/next get updated
        """
        print self.conditionset
        query.condition_factory('condition', self.conditionset, self.counter)
        remainingChild = self.conditionset[0] #will check it has updated
        self.counter +=1
        query.condition_factory('condition', self.conditionset, self.counter, self.conditionset.firstObj)
        self.assertEqual(self.conditionset.firstID, self.conditionset[0].condID)
        self.assertEqual(self.conditionset[1].prevID, self.conditionset[0].condID)
        self.assertEqual(self.conditionset[0].nextID, self.conditionset[1].condID)
        #check index exists
        self.assertTrue(self.conditionset[1])
        #remove last added child
        result = self.conditionset.remove_child(self.counter)
        self.assertEqual(result, True)
        #check it's gone
        with self.assertRaises(IndexError):
            self.conditionset[1]
        #check values have changed
        self.assertEqual(self.conditionset.firstID, remainingChild.condID)
        self.assertEqual(self.conditionset[0].condID, remainingChild.condID)
        self.assertEqual(self.conditionset[0].nextID, None)
        self.assertEqual(self.conditionset[0].nextObj, None)
        self.assertEqual(self.conditionset[0].prevID, None)
        self.assertEqual(self.conditionset[0].prevObj, None)

    def test_find_parent_set(self):
        """
        Test the parent set finder. It uses an id.
        """
        query.condition_factory('condition', self.conditionset, self.counter)
        self.counter +=1
        query.condition_factory('set', self.conditionset, self.counter)
        subSetID = self.counter
        self.counter +=1
        subset = query.find_set(subSetID, self.conditionset)
        query.condition_factory('set', subset, self.counter)
        subSubSetID = self.counter
        self.counter +=1
        query.condition_factory('condition', self.conditionset, self.counter, self.conditionset.firstObj)
        result = query.find_set(subSubSetID, self.conditionset) #checks for a set inside a set which is inside a master set
        self.assertEqual(result.condID, subSubSetID)
        
if __name__ == '__main__':
    unittest.main()
