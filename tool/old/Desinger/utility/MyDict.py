__author__ = 'Administrator'

class MyDict(dict):
    def __init__(self,preGet = None,postGet = None,preSet = None,postSet = None,preDel = None,postDel = None):
        self._preGet  = preGet
        self._postGet = postGet
        self._preSet  = preSet
        self._postSet = postSet
        self._preDel  = preDel
        self._postDel = postDel

    def __getitem__(self, key):
        if self._preGet:
            self._preGet()

        value = self[key]

        if self._postGet:
            self._postGet()

        return value

    def __setitem__(self, key, value):
        if self._preSet:
            self._preSet()

        dict.__setitem__(self,key,value)

        if self._postSet:
            self._postSet()

    def __delitem__(self, key):
        if self._preDel:
            self._preDel()

        dict.__delitem__(self,key)

        if self._postDel:
            self._postDel