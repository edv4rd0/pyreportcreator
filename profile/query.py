"""
This module contains classes for the building blocks of a class definition.
These are used by the Query class for defining the query.

"""
#-------------------------------------------------------------


class AbstractCondition(object):
    """
    Defines an abstract class for condition elements to inherit from
    """
    condID = None
    parentObj = None
    parentID = None
    prevID = None
    prevObj = None
    nextID = None
    nextObj = None

    def __init__(self, condID, parent = None, prev = None):
        if parent != None:
            self.parentObj = parent
            self.parentID = self.parentObj.condID
        if prev != None:
            self.prevObj = prev
            self.prevID = prev.condID
        self.condID = condID

class Condition(AbstractCondition):
    """
    Defines a condition (a la, column LIKE '%term')
    """
    field1 = tuple()
    columnType = ""
    field2 = tuple()
    operator = None
    
    def __init__(self, condID, parent = None, prev = None):
        AbstractCondition.__init__(self, condID, parent, prev)

    def configure_condition(self, field1, field2, condition):
        """
        Configure condition.
        @Params:
        field1 is always a tuple specifying a column (tableName, columnName)
        field one is either a tuple or a string. If tuple it's specifying a column. If string, a value.
        condition is an operator like '<', or a text based one: 
        """
        self.field1 = field1
        self.field2 = field2
        self.operator = condition

    def move(self, newParent):
        """Move condition to a new parent"""
        temp = self
        self.remove_child(self.condID)
        temp.prevObj = None
        temp.prevID = None
        temp.nextObj = None
        temp.nextID = None
        temp.parentObj = newParent
        temp.parentID = newParent.condID
        newParent.add_child_member(temp)

    def remove_self(self):
        self.parentObj.remove_child(self.condID)

#-------------------------------------------------------------

class ConditionSet(AbstractCondition):
    """
    Defines a set of conditions. It's a container for related conditions which are seperated using OR, AND and NOT.
    """
    firstID = None
    firstObj = None
    boolVal = None
    conditions = list()
    

    def __init__(self, condID, parent = None, prev = None, boolVal = 'and'):
        """
        Initializes the set. Basically, if everything is None it's the first set.
        """
        AbstractCondition.__init__(self, condID, parent, prev)
        self.boolVal = boolVal
        self.conditions = []
    
    def add_child_member(self, item):
        """
        This method appends a member condition or child set to the set.
        """
        if len(self.conditions) > 0:
            if item.prevObj != None:
                item.prevID = item.prevObj.condID
                if item.prevObj.nextObj != None:
                    item.nextID = item.prevObj.nextID
                    item.nextObj = item.prevObj.nextObj
                    item.nextObj.prevID = item.condID
                    item.nextObj.prevObj = item    
                item.prevObj.nextID = item.condID
                item.prevObj.nextOBj = item
            elif item.prevID == None: #prev == none, means it's now first in sequence
                self.firstObj.prevID = item.condID
                self.firstObj.prevObj = item
                item.nextObj = self.firstObj
                item.nextID = self.firstID
                self.firstObj = item
                self.firstID = item.condID
        elif len(self.conditions) == 0:
            self.firstID = item.condID
            self.firstObj = item
        self.conditions.append(item)
        return item

    def update_pointers(self, item):
        """
        Update next, first and prev pointers.
        This is used when removing objects from a ConditionSet
        """
        if item.parentObj != None:
            if item.parentObj.firstID == item.condID:
                #if removing the first object in the set of coditions
                try:
                    item.nextObj.prevID = None
                    item.nextObj.prevObj = None
                    item.parentObj.firstID = item.nextID
                    item.parentObj.firstObj = item.nextObj
                except AttributeError: #no nextObj
                    item.parentObj.firstID = None
                    item.parentObj.firstObj = None
            else:
                #this object is in the middle of a sequence of objects
                if item.nextObj != None:
                    item.nextObj.prevID = item.prevID
                    item.nextObj.prevObj = item.prevObj
                if item.prevObj != None:
                    item.prevObj.nextID = item.nextID
                    item.prevObj.nextObj = item.nextObj
        else:
            if item.nextObj != None:
                item.nextObj.prevID = item.prevID
                item.nextObj.prevObj = item.prevObj
            if item.prevObj != None:
                item.prevObj.nextID = item.nextID
                item.prevObj.nextObj = item.nextObj
            
    def remove_child(self, id):
        """
        Remove a child. Even if a set.
        """
        for i in self.conditions:
            if id == i.condID:
                self.update_pointers(i)
                index = self.conditions.index(i)
                del self.conditions[index]
                return True
        return False

    def remove_self(self):
        self.parentObj.remove_child(self.condID)

#-------------------------------------------------


def find_set(parentID, theset):
    """
    This method iterates through the sets recursively until it find the correct parent
    """
    for i in theset.conditions:
        if i.condID == parentID:
            return i
        elif isinstance(i, ConditionSet):
            j = find_set(parentID, i)
            if j != False:
                return j
    return False
        
def condition_factory(type, condID, parentObj = None, prev = None, boolVal = None):
    """
    Creates conditions and sets
    """
    if type == "set":
        if parentObj != None:
            cond = parentObj.add_child_member(ConditionSet(condID, parentObj, prev, boolVal))
            return cond
        else:
            return ConditionSet(condID, parentObj, prev, boolVal)
    elif type == "condition":
        if parentObj != None:
            cond = parentObj.add_child_member(Condition(condID, parentObj, prev))
            return cond
        else:
            return Condition(condID, parentObj, prev)

