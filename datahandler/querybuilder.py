import datahandler
import sqlalchemy
from sqlalchemy import select
from sqlalchemy.sql import and_, or_, not_
from pyreportcreator.profile import profile, query

class ClauseException(Exception):
    """Raise this if there is an error in building the where clause"""
    def __init__(self, var = "Where Clause Fail"):
        self.var = var

class ConditionException(Exception):
    """If there is a failure in building a condition this is raised"""
    def __init__(self, var = "Condition Fail"):
        self.var = var

class NoConditionsException(Exception):
    """If there are no conditions set at all this is raised"""
    def __init__(self, var = "No conditions set"):
        self.var = var

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
    elif isinstance(condition.field2, profile.Query):
        field2 = build_query(condition.field2)
        if field2 == False:
            raise ConditionException()
    elif condition.field2 != None:
        field2 = condition.field2
    else:
        raise ConditionException()
    #compile condition:
    if condition.operator == "==":
        return field1==field2
    elif condition.operator == ">":
        return field1>field2
    elif condition.operator == "<":
        return field1<field2
    elif condition.operator == "NOT":
        return field1.not_(field2)
    elif condition.operator == "NOT IN":
        return ~field1.in_(field2)
    elif condition.operator == "LIKE":
        return field1.like_("%"+field2)
    elif condition.operator == "IS IN":
        return field1.in_(field2)
    elif condition.operator == "BETWEEN":
        return field1.between_(field2[0], field2[1])
    elif condition.operator == "NOT BETWEEN":
        return ~field1.between_(field2[0], field2[1])
    else:
        raise ConditionException()


def return_where_conditions(condObj, engineID):
    """
    Build the where condition.

    This function concatenates sqlalchemy columns and subqueries
    together. It also converts string representations of operators
    into SQLAlchemy operators
    @params:
    condObj is a condition object. It's either an instance of
    Condition or ConditionSet. This is a recursive function to
    iterate over and concatenate all of the conditions. As such,
    it is started with condObj = query.condition.firstObj.
    """

    if isinstance(condObj, query.ConditionSet): #if the thing is a condition set
        try:
            if condObj.boolVal == 'and':
                v = return_where_conditions(condObj.firstObj, engineID)
                return and_(*v), return_where_conditions(condObj.nextObj, engineID) #put brackets around a condition 'set'
            elif condObj.boolVal == 'or':
                v = return_where_conditions(condObj.firstObj, engineID)
                return or_(*v), return_where_conditions(condObj.nextObj, engineID)
        except AttributeError:
            try:
                if condObj.boolVal == 'and':
                    a = return_where_conditions(condObj.firstObj, engineID)
                    return and_(*a)
                elif condObj.boolVal == 'or':
                    a = return_where_conditions(condObj.firstObj, engineID)
                    return or_(*a)
            except ConditionException:
                raise ClauseException() #We have to fail, because otherwise we will be running an improperly built query
        except ConditionException:
            raise ClauseException()
    else:
        try:
            return get_condition(condObj, engineID), return_where_conditions(condObj.nextObj, engineID)
        except AttributeError:
            try:
                return get_condition(condObj, engineID)
            except ConditionException:
                raise ClauseException()
        except ConditionException:
            raise ClauseException


def build_query(query):
    """
    Builds query by creating all objects based on the unicode 
    string descriptors stored in the query object
    """
    columns = []
    for t in query.selectItems.keys():
        if isinstance(query.selectItems[t], profile.Query):
            subquery = build_query(query.selectItems[t])
            columns.append(subquery.label(query.selectItems[t]._name)) #a scalar select
        else:
            for c in query.selectItems[t]:
                columns.append(datahandler.DataHandler.get_column_object(t, query.engineID, c[0]))
    SQLAQuery = select(columns)
    if len(query.conditions.conditions) > 0: #check if query has any WHERE conditions, if so, build where clause
        SQLAQuery = SQLAQuery.where(return_where_conditions(query.conditions, query.engineID))
    return SQLAQuery
