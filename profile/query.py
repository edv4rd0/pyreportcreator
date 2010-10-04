"""
This module contains classes for the building blocks of a class definition.
These are used by the Query class for defining the query.

"""
#-------------------------------------------------------------


class Condition(object):
    """
    Defines a condition (a la, column LIKE '%term')
    """
    condID = None
    parent = None
    field1 = ""
    field2 = tuple()
    operator = ""
    prevID = None
    prevObj = None
    nextID = None
    nextObj = None
    joiningBool = None
    
    def __init__(self, condID, parent = None):
        self.parent = parent
        self.condID = id

    def configure_condition(self, field1, field2, condition, join):
        """
        Configure condition.
        @Params:
        field1 is always a tuple specifying a column (tableName, columnName)
        field one is either a tuple or a string. If tuple it's specifying a column. If string, a value.
        condition is an operator like '<', or a text based one: 
        """
        self.field1 = field1
        self.field2 = field2
        self.condition = condition
        self.joiningBool == join

#-------------------------------------------------------------

class ConditionSet(list):
    """
    Defines a set of conditions. It's a container for related conditions which are seperated using OR, AND and NOT.
    """
    firstID = None
    firstObj = None
    parent = None
    prevID = None
    prevObj = None
    nextID
    nextObj = None
    boolVal = None
    condID = None
    def __init__(self, condID, parent = None, prev = None, boolVal = None):
        """
        Initializes the set. Basically, if everything is None it's the first set.
        """
        super( ConditionSet, self ).__init__()
        self.parent = parent
        self.condID = condID
        if prev != None:
            self.prevObj = prev
            self.prevID = prev.condID
    
    def add_child_member(self, item):
        """
        This method appends a member condition or child set to the set.
        """
        if size(self) > 0 and self.firstID != item.nextID:
            for i in self:
                if item.nextID == i[1].nextID:
                    i[1].nextID = item.condID
                    i[1].nextObj = item
                    break
        if item.nextID == self.firstID:
            self.firstID == item.condID
            self.firstObj == item
        self.append((item.condID, item))
        return True

    def remove_child_condition(self, item):
        """
        remove a child condition
        """
        itemIndex = self.index(item)
        for j in self:
            if id == j[1].prev:
                j[1].prev = i[1].prev
                break
            self.remove(i)
            return True

    def remove_child_set(self, item):
        """
        Remove a child set
        """
        itemIndex = self.index(i)
        for j in self:
            if id == j[1].prev:
                j[1].prev = i[1].prev
                break
        self.remove(i)
        return True


    def remove_child(self, id):
        """
        Remove a child. Even if a set.
        """
        for i in self:
            if id == i[0] and isinstance(i[1],Condition):
                remove_child_condition(i)
                return True
            if id == i[0] and isinstance(i[1], ConditionSet):
                remove_child_set(i)
                return True

    def remove_self(self):
        self.parent.remove_child(id)

#-------------------------------------------------


def find_set(parentID, theset):
    """
    This method iterates through the sets recursively until it find the correct parent
    """
    for i in theset:
        if i[0] == parentID:
            return i[1]
        elif isinstance(i[1], ConditionSet):
            j = find_set(parentID, i[1])
            if j != False:
                return j
    return False
        
def ConditionFactory(type, parentObj = None, parentID = None, prev = None, boolVal = None):
    """
    Creates conditions and sets
    """
    if type == "set":
        if parentObj != None:
            parentObj.add_child_member(ConditionSet(parentID, prev, boolVal))
            return True
        else:
            return ConditionSet(parentID, prev, boolVal)
    elif type == "condition":
        if parentObj != None:
            parentObj.add_child_member(Condition(parentID, prev, boolVal))
            return True
        else:
            return Condition(parentID, prev, boolVal)

