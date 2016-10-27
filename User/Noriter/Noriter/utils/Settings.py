from PySide import QtCore

class Settings(object):
	_instance = None
	_isInit   = False
	def __new__(cls, group=None):
		if not Settings._instance:
			Settings._instance = super(Settings,cls).__new__(cls)

		Settings._instance.group = group
		return Settings._instance

	def __init__(self,group=None):
		if Settings._isInit:
			return
		Settings._isInit = True

		self.db = QtCore.QSettings("Nooslab", "Noriter")

	def __setitem__(self,key,value):
		if value :
			self.db.setValue(key,value)
			
	def __getitem__(self,key):
		return self.db.value(key)

	def __delitem__(self,key):
		self.db.remove(key)

	def __enter__(self):
		self.db.beginGroup(self.group)
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.db.endGroup()

	def keys(self):
		return self.db.childKeys()

	def groups(self):
		return self.db.childGroups()

	def clear(self):
		self.db.clear()