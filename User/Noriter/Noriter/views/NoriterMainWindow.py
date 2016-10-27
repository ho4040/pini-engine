from ..UI.Layout import *
from ..UI import MainWindow as nMain
from .PluginListWindow import *
from PySide import QtCore

class NoriterMain(nMain.MainWindow):
	DOCK_LEFT	 =  QtCore.Qt.LeftDockWidgetArea
	DOCK_RIGHT	 =  QtCore.Qt.RightDockWidgetArea
	DOCK_TOP 	 =  QtCore.Qt.TopDockWidgetArea
	DOCK_BOTTOM  =  QtCore.Qt.BottomDockWidgetArea

	_instance = None
	_isInit   = False
	def __new__(cls, *args, **kwargs):
		if not NoriterMain._instance:
			NoriterMain._instance = super(NoriterMain,cls).__new__(cls,*args,**kwargs)

		return NoriterMain._instance

	def __init__(self):
		if NoriterMain._isInit:
			return
			
		super(NoriterMain,self).__init__()
		NoriterMain._isInit = True

		self.docks = {}

	def Dock(self,position,widget,tabify=True):
		print "9_4_0"
		self.addDockWidget(position,widget)
		print "9_4_1"
		widget.setFloating(False)
		print "9_4_2"
		if tabify : 
			print "9_4_2-1"
			if position in self.docks : 
				print "9_4_2-1-1"
				self.tabifyDockWidget(self.docks[position],widget);

		print "9_4_3"
		self.docks[position] = widget
		print "9_4_4"

	def SetMain(self,widget):
		self.setCentralWidget(widget)

	"""
	@MenuBar("plugin/list")
	def new():
		PluginListWindow()
	"""

	@LayoutGUI
	def GUI(self):
		pass