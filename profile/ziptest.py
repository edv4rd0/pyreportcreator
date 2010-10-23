import zipfile
import jsonpickle
import profile
import query
from pyreportcreator.datahandler import datahandler

connID = datahandler.ConnectionManager.create_new_data_connection(databaseType = 'mysql', address = 'localhost', dbname = 'store', user = 'pytest', password = 'P@ssw0rd')
datahandler.DataHandler.add(connID)


#Single table query with nested conditions
queryObjNested = profile.Query(1, connID, "Test Query")
queryObjNested.add_select_item('tblproduct', 'productID')
queryObjNested.add_select_item('tblproduct', 'name')
queryObjNested.add_select_item('tblproduct', 'ISBN')
queryObjNested.add_select_item('tblproduct', 'price')
## We will access the objects directly - profile Query object interface not up to it
#query.condition_factory('set', 1, queryObjConditions.conditions, None, 'or')
queryObjNested.conditions.boolVal = 'and'
  
query.condition_factory('set', 1, queryObjNested.conditions, None, 'or')
query.condition_factory('set', 2, queryObjNested.conditions, None, 'or')

query.condition_factory('condition', 3, queryObjNested.conditions.firstObj)
query.condition_factory('condition', 4, queryObjNested.conditions.firstObj)
query.condition_factory('condition', 5, queryObjNested.conditions.firstObj.nextObj)
query.condition_factory('condition', 6, queryObjNested.conditions.firstObj.nextObj)
queryObjNested.conditions.firstObj.firstObj.configure_condition(('tblproduct', 'price'), 13, '>')
queryObjNested.conditions.firstObj.firstObj.nextObj.configure_condition(('tblproduct', 'productID'), 5L, '==')
queryObjNested.conditions.firstObj.nextObj.firstObj.configure_condition(('tblproduct', 'price'), 13, '>')
queryObjNested.conditions.firstObj.nextObj.firstObj.nextObj.configure_condition(('tblproduct', 'productID'), 5L, '==')

pickled = jsonpickle.encode(queryObjNested)
print pickled


zf = zipfile.ZipFile('zipped_pickle.zip', 'w', zipfile.ZIP_DEFLATED)
zf.writestr('data.pkl', pickled)

print "\n\n"
#zf.open('data.pkl').read()

unpickled = jsonpickle.decode(zf.open('data.pkl').read())

print unpickled


print unpickled.conditions.firstObj.nextObj.firstObj

def save_doc(self, document):
    zf = zipfile.ZipFile(self.__file, 'w', zipfile.ZIP_DEFLATED)
    pickled = jsonpickle.encode(document)
    zf.writestr(str(document.documentID), pickled)

def load_doc(self, docID):
    zf = zipfile.ZipFile(self.__file, 'w', zipfile.ZIP_DEFLATED)
    unpickled = jsonpickle.decode(zf.open(str(docID)).read()
    for i in unpickled.conditions.conditions:
    if i.condID == unpickled.conditions.firstID:
        unpickled.conditions.firstObj = i
        i.parentObj = unpickled.conditions
        for j in unpickled.conditions.conditions:
            if j.condID == i.nextID:
                j.prevObj == i
                i.nextObj == j
            elif i.condID == j.nextID:
                i.prevObj == j
                j.nextObj == i

