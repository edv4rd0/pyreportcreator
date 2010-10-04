import datahandler
import sqlalchemy
from pyreportcreator.profile import profile

def run_report(report):
    queries = dict()
    for query in report.queries:
        queries[query.engineID, query._name] = build_query(query)
    #will have to sort out some means of reading it line by line into a csv file

def get_condition(condition, engineID):
    """
    This accepts an object of class Condition (my own) and turns
    it into an SQLAlchemy condition which the SQL Expression
    Engine of sqlalchemy would accept.

    The condition object contains the needed condition definition.
    """
    field1 = datahandler.DataHandler.get_column_object(condition.field1[0], engineID, condition.field1[1])
    if isinstance(condition.field2, tuple):
        #TODO: add proper error checking code here
        if condition.field2[0] == "column":
            field2 = datahandler.DataHandler.get_column_object(condition.field1[1], engineID, condition.field2[2])
        if condition.field2[0] == "range": #range of values, for an IN statement
            field2 = condition.field2[1]
        else:
            field2 = (condition.field2[1], condition.field2[2]) #two values, for a BETWEEN statement
    elif isinstance(condition.field2, string):
        field2 = condition.field2
    elif isinstance(condition.field2, profile.Query):
        field2 = build_query(condition.field2)
        if field2 == False:
            return False
    else: 
        return False
    #compile condition:
    if condition.operator == "==":
        SQLACondition = field1==field2
    elif condition.operator == ">":
        SQLACondition = field1>field2
    elif condition.operator == "<":
        SQLACondition = field1<field2
    elif condition.operator == "NOT":
        SQLACondition = field1.not_(field2)
    elif condition.operator == "NOT IN":
        SQLACondition = ~field1.in_(field2)
    elif condition.operator == "LIKE":
        SQLACondition = field1.like_("%"+field2)
    elif condition.operator == "IS IN":
        SQLACondition = field1.in_(field2)
    elif condition.operator == "BETWEEN":
        SQLACondition = field1.between_(field2[0], field2[1])
    elif condition.operator == "NOT BETWEEN":
        SQLACondition = ~field1.between_(field2[0], field2[1])
    else:
        return False
    return (SQLACondition, condition.boolVal)


def concatenate_where_conditions(condObj, engineID):
    """
    This function concatenates sqlalchemy columns and subqueries
    together. It also converts string representations of operators
    into SQLAlchemy operators
    @params:
    condObj is a condition object. It's either an instance of
    Condition or ConditionSet. This is a recursive function to
    iterate over and concatenate all of the conditions. As such,
    it is started with condObj = query.condition.firstObj.
    """
    if isinstance(condObj, list): #if the thing is a condition set
        result = (concatenate_where_conditions(condObj.firstObj, engineID)) #put brackets around a condition 'set'
        if result == False:
            return False #failure
        if condObj.nextObj != None:
            sedondPart = concatenate_where_conditions(condObj.nextObj, engineID)
            if result == False:
                return False #failure
    else:
        result = get_condition(startObj, engineID)
        if result == False:
            return False
        if startObj.nextObj != None:
            secondPart = concatenate_where_conditions(condObj.nextObj, engineID)
    try:        
        if result[1] != None:
            SQLAWhere = result[0] secondPart
        elif result[1] == "&":
            SQLAWhere = & result[0] secondPart
        elif result[1] == "|":
            SQLAWhere = | result[0] secondPart
        elif result[1] == "~":
            SQLAWhere = ~result[0] secondPart
        else:
            return result[1] secondPart
    except IndexError:
        print "index error:"
        return False

def build_query(self, query):
    """
    Builds query by creating all objects based on the unicode 
    string descriptors stored in the query object
    """
    columns = []
    for t in query.selectItems.keys():
        if isinstance(query.selectItems[t], string):
            for c in query.selectItems[t]:
                columns.append(datahandler.DataHandler.get_column_object(t, query.engineID, c))
        else: #it's a subquery
            subquery = build_query(query.selectItems[t])
            columns.append(subquery.label(query.selectItems[t]._name)) #a scalar select
            
    SQLAQuery = select(columns).where(concatenate_where_conditions(query.condition.firstObj, query.engineID)
    
    return SQLAquery


