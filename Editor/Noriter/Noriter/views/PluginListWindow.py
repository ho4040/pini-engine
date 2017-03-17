from PySide import QtGui

from ..UI.Layout import *
from ..UI import Window as nWin
from ..plugin.ModuleRefresher import *
from ..utils.Settings import *


class PluginListWindow(nWin.Window):
	_instance = None
	_isInit   = False
	def __new__(cls, *args, **kwargs):
		if not PluginListWindow._instance:
			PluginListWindow._instance = super(PluginListWindow,cls).__new__(cls,*args,**kwargs)

		return PluginListWindow._instance

	def __init__(self):
		if PluginListWindow._isInit:
			self.show();
			return
		PluginListWindow._isInit = True

		super(PluginListWindow, self).__init__()

		self.modules = {}
		self.currentSelected = []

		moduleList = []
		with Settings("Noriter"):
			with Settings("Plugins") as db:
				for path in db.keys():
					moduleList.append( db[path] )
					
		for p in moduleList:
			self.addModule( p )

	@LayoutGUI
	def GUI(self):
		self.plugins = self.Layout.listbox(self.listFactory,[])
		self.plugins.changed.connect(self.onCurrentSelected)
		self.Layout.button("add",self.addClicked)
		self.Layout.button("remove",self.removeClicked)

	def addClicked(self):
		path = QtGui.QFileDialog.getExistingDirectory()
		if path : 
			self.addModule(path)
			with Settings("Noriter"):
				with Settings("Plugins") as db:
					db[str(len(db.keys()))] = path

	def removeOnDB(self,path):
		with Settings("Noriter"):
			with Settings("Plugins") as db:
				for p in db.keys():
					if db[p] == path : 
						del db[ p ]
						return 

	def removeClicked(self):
		for selected in self.currentSelected:
			del self.modules[selected]
			self.removeOnDB(selected)
		
		if len(self.currentSelected) > 0:
			self.plugins.data = self.modules.keys()
			self.currentSelected = []

	def addModule(self,path):
		mr = ModuleRefresher()
		mr.addReference(path)
		mr.setPath(path)
		self.modules[path] = mr
		self.plugins.data  = self.modules.keys()

	def onCurrentSelected(self,widgets):
		self.currentSelected = []
		for widget in widgets:
			self.currentSelected.append(widget.data)

	def listFactory(self,data):
		label = self.Layout.label(data)
		return 20