import pyreportcreator.datahandler
def find_set(parentID, theset):
    """
    This method iterates through the sets recursively until it find the correct parent
    """
    for i in theset:
        print i
        if i[0] == parentID:
            return i[1]
        elif isinstance(i[1], list):
            j = find_set(parentID, i[1])
            if j != False:
                print "yo"
                return j            
    return False

testlist = [('1',[('2',"jfdkdfkfdk"),('3',[1,2,3,4,5])]),('8',[4,7])]

print find_set('3', testlist)
