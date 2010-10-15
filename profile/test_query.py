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
        self.assertEqual(len(self.conditionset.conditions), 0)
        self.counter = 1


    def test_add_condition_to_conditionset(self):
        """
        Test whether a simple condition can be added to the condition set
        """
        query.condition_factory('condition', self.counter, self.conditionset)
        self.assertTrue(self.conditionset.conditions[0])
        self.assertIsInstance(self.conditionset.firstObj, query.Condition)
        self.assertIsInstance(self.conditionset.conditions[0], query.Condition)
        self.assertEqual(self.conditionset.firstObj.condID, self.counter)

    def test_firstID_is_set(self):
        """
        Test whether the conditionset updates it's pointer to the first condition in the conditionset
        """
        query.condition_factory('condition', self.counter, self.conditionset)
        self.assertEqual(self.conditionset.firstID, self.conditionset.conditions[0].condID)
        self.assertNotEqual(self.conditionset.firstObj, None)

    def test_prev_next_continuity_on_add(self):
        """
        Test whether upon adding a second condition to a condition set the prev and next IDs get updated
        and the firstID gets changed. The condition's place is not set in this test. (defaults to first)
        """
        self.assertEqual(len(self.conditionset.conditions), 0)
        query.condition_factory('condition', self.counter, self.conditionset)
        self.assertEqual(self.conditionset.firstID, self.conditionset.conditions[0].condID)
        self.counter +=1
        query.condition_factory('condition', self.counter, self.conditionset)
        self.assertEqual(self.conditionset.firstID, self.conditionset.conditions[1].condID)
        #one added second should be first (rule: prev == None, they are first
        self.assertEqual(self.conditionset.conditions[0].prevID, self.conditionset.conditions[1].condID)
        self.assertEqual(self.conditionset.conditions[1].nextID, self.conditionset.conditions[0].condID)

    def test_prev_next_continuity_add_child_member(self):
        """
        Test whether upon adding a second condition to a condition set the prev and next IDs get updated
        and the firstID gets changed. The condition's place is set in this test.

        THIS TESTS THE add_child_member() METHOD DIRECTLY
        """
        self.conditionset.add_child_member(query.Condition(self.counter, self.conditionset))
        self.counter +=1
        self.conditionset.add_child_member(query.Condition(self.counter, self.conditionset, self.conditionset.firstObj))
        self.assertEqual(self.conditionset.firstID, self.conditionset.conditions[0].condID)
        self.assertEqual(self.conditionset.conditions[1].prevID, self.conditionset.conditions[0].condID)
        self.assertEqual(self.conditionset.conditions[0].nextID, self.conditionset.conditions[1].condID)

    def test_prev_next_continuity_on_add_with_place(self):
        """
        Test whether upon adding a second condition to a condition set the prev and next IDs get updated
        and the firstID gets changed. The condition's place is set in this test.
        """
        query.condition_factory('condition', self.counter, self.conditionset)
        self.counter +=1
        query.condition_factory('condition', self.counter, self.conditionset, self.conditionset.firstObj)
        self.assertEqual(self.conditionset.firstID, self.conditionset.conditions[0].condID)
        self.assertEqual(self.conditionset.conditions[1].prevID, self.conditionset.conditions[0].condID)
        self.assertEqual(self.conditionset.conditions[0].nextID, self.conditionset.conditions[1].condID)

    def test_remove_works(self):
        """
        This test simply tests that the remove method does remove the child
        """
        query.condition_factory('condition', self.counter, self.conditionset)
        self.counter +=1
        query.condition_factory('condition', self.counter, self.conditionset)
        #check index exists
        self.assertTrue(self.conditionset.conditions[1])
        #remove
        result = self.conditionset.remove_child(self.counter)
        self.assertEqual(result, True)
        #check it's gone
        with self.assertRaises(IndexError):
            self.conditionset.conditions[1]

    def test_prev_next_continuity_on_remove(self):
        """
        Test whether upon deleteing a child the pointers to prev/next get updated
        """
        query.condition_factory('condition', self.counter, self.conditionset)
        remainingChild = self.conditionset.conditions[0] #will check it has updated
        self.counter +=1
        query.condition_factory('condition', self.counter, self.conditionset, self.conditionset.firstObj)
        self.assertEqual(self.conditionset.firstID, self.conditionset.conditions[0].condID)
        self.assertEqual(self.conditionset.conditions[1].prevID, self.conditionset.conditions[0].condID)
        self.assertEqual(self.conditionset.conditions[0].nextID, self.conditionset.conditions[1].condID)
        #check index exists
        self.assertTrue(self.conditionset.conditions[1])
        #remove last added child
        result = self.conditionset.remove_child(self.counter)
        self.assertEqual(result, True)
        #check it's gone
        with self.assertRaises(IndexError):
            self.conditionset.conditions[1]
        #check values have changed
        self.assertEqual(self.conditionset.firstID, remainingChild.condID)
        self.assertEqual(self.conditionset.conditions[0].condID, remainingChild.condID)
        self.assertEqual(self.conditionset.conditions[0].nextID, None)
        self.assertEqual(self.conditionset.conditions[0].nextObj, None)
        self.assertEqual(self.conditionset.conditions[0].prevID, None)
        self.assertEqual(self.conditionset.conditions[0].prevObj, None)

    def test_find_parent_set(self):
        """
        Test the parent set finder. It uses an id.
        """
        query.condition_factory('condition', self.counter, self.conditionset)
        self.counter +=1
        query.condition_factory('set', self.counter, self.conditionset)
        #print self.conditionset
        subSetID = self.counter
        self.counter +=1
        subset = query.find_set(subSetID, self.conditionset)
        query.condition_factory('set', self.counter, subset)
        subSubSetID = self.counter
        self.counter +=1
        query.condition_factory('condition', self.counter, self.conditionset, self.conditionset.firstObj)
        result = query.find_set(subSubSetID, self.conditionset) #checks for a set inside a set which is inside a master set
        self.assertEqual(result.condID, subSubSetID)
        
if __name__ == '__main__':
    unittest.main()
