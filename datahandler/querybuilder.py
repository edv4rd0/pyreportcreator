import datahandler
import sqlalchemy
from sqlalchemy import select
from sqlalchemy.sql import and_, or_, not_
from pyreportcreator.profile import profile, query
import csv

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

class JoinException(Exception):
    """If the join is not fully configured, raise this exception."""
    def __init__(self, var = "Join not configured correctly"):
        self.var = var


def run_report(query, engineId, fileName = 'test.csv', headings = None):
    """Write query results to CSV file"""
    csvOut = csv.writer(open(fileName, 'wb'),  dialect='excel')
    # execute query
    if headings:
        csvOut.writerow(headings)
    offset = 0
    s = query.limit(1)
    result = datahandler.ConnectionManager.dataConnections[engineId].execute(s)
    for row in result:
        csvOut.writerow(row)
    offset = 1
    while True:
        s = query.offset(offset).limit(1000)
        result = datahandler.ConnectionManager.dataConnections[engineId].execute(s)
        for row in result:
            csvOut.writerow(row)
        if result.rowcount < 1000:
            break
        offset += 1000
    

def get_condition(condition, engineID):
    """
    This accepts an object of class Condition (my own) and turns
    it into an SQLAlchemy condition which the SQL Expression
    Engine of sqlalchemy would accept.

    The condition object contains the needed condition definition.
    """
    try:
        field1 = datahandler.DataHandler.get_column_object(condition.field1[0], engineID, condition.field1[1])
        if isinstance(condition.field2, list):
            #TODO: add proper error checking code here
            if condition.field2[0] == "column":
                field2 = datahandler.DataHandler.get_column_object(condition.field1[1], engineID, condition.field2[2])
            if condition.field2[0] == "range": #range of values, for an IN statement
                field2 = condition.field2[1]
            else:
                field2 = (condition.field2[0], condition.field2[1]) #two values, for a BETWEEN statement
        elif isinstance(condition.field2, profile.Query):
            field2 = build_query(condition.field2)
            if field2 == False:
                raise ConditionException()
        elif condition.field2 != None:
            field2 = condition.field2
        else:
            raise ConditionException()
    except IndexError:
        raise ConditionException()
    #compile condition:
    if condition.operator == "==":
        return field1==field2
    elif condition.operator == "!=":
        return ~(field1==field2)
    elif condition.operator == ">":
        return field1>field2
    elif condition.operator == "<":
        return field1<field2
    elif condition.operator == "NOT":
        return field1.not_(field2)
    elif condition.operator == "NOT IN":
        return ~field1.in_(field2)
    elif condition.operator == "LIKE":
        return field1.like("%"+field2)
    elif condition.operator == "IS IN":
        return field1.in_(field2)
    elif condition.operator == "BETWEEN":
        return field1.between(field2[0], field2[1])
    elif condition.operator == "NOT BETWEEN":
        return ~field1.between(field2[0], field2[1])
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
    conditions = []
    itrCond = condObj
    while itrCond:
        if isinstance(itrCond, query.ConditionSet): #if the thing is a condition set
            try:
                if itrCond.firstObj == None:
                    pass
                elif itrCond.firstObj.nextObj == None:
                    conditions.append(return_where_conditions(itrCond.firstObj, engineID))
                else:
                    if itrCond.boolVal == 'and':
                        v = return_where_conditions(itrCond.firstObj, engineID)
                        try:
                            conditions.append(and_(*v))
                        except TypeError: #length of v is one
                            conditions.append(v)
                    elif itrCond.boolVal == 'or':
                        v = return_where_conditions(itrCond.firstObj, engineID)
                        try:
                            conditions.append(or_(*v))
                        except TypeError: #length of v is one
                            conditions.append(v)
            except ConditionException:
                raise ClauseException()
        else:
            try:
                conditions.append(get_condition(itrCond, engineID))
            except ConditionException:
                raise ClauseException()
        itrCond = itrCond.nextObj #increment
    #return result set
    if len(conditions) == 1:
        return conditions[0] #otherwise it will unpack one value from the list correctly
    return conditions


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
    try:
        join = query.joins
        #check join type
        leftTable = datahandler.DataHandler.get_table_object(join[1][0], query.engineID)
        joinTable = datahandler.DataHandler.get_table_object(join[2][0], query.engineID)
        leftCol = datahandler.DataHandler.get_column_object(join[1][0], query.engineID, join[1][1])
        rightCol = datahandler.DataHandler.get_column_object(join[2][0], query.engineID, join[2][1])
        if join[0] == 'left':
            if join[3] == '==':
                SQLAQuery = select(columns, from_obj = [leftTable.outerjoin(joinTable, leftCol==rightCol)])
        elif join[0] == 'inner':
            if join[3] == '==':
                SQLAQuery = select(columns, from_obj = [leftTable.join(joinTable, leftCol==rightCol)])
    except IndexError:
        SQLAQuery = select(columns)

    if len(query.conditions.conditions) > 0: #check if query has any WHERE conditions, if so, build where clause
        try:
            SQLAQuery = SQLAQuery.where(*return_where_conditions(query.conditions, query.engineID))
        except TypeError: #length of conditions returned is one
            SQLAQuery = SQLAQuery.where(return_where_conditions(query.conditions, query.engineID))
    return SQLAQuery
