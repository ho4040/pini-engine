# -*- coding: utf-8 -*-

import os
import shutil

from PySide.QtGui import *
from PySide.QtCore import *

from controller.LayerController import *
from controller.ComponentController import *

from windows.DesignerMain import DesignerMain
from uic.Ui_PropertyDock import Ui_PropertyDock
from utility.QtUtils import *
from widget.AddComponent import *

class PropertyDock(QDockWidget,Ui_PropertyDock):
	def __init__(self,parent=None):
		super(PropertyDock,self).__init__(parent)
		self.setupUi(self)
		self.destroyUI();

		self.selectModels = None

		#connect
		self.ui_AddComponent.clicked.connect( self.uicall_AddComponent )

		LayerController.getInstance().focusChanged.connect( self.OnFocusObject )
		ComponentController.getInstance().componentAdded.connect( self.OnRebuildComponentUI )
		ComponentController.getInstance().componentDeleted.connect( self.OnRebuildComponentUI )

	def OnRebuildComponentUI(self):
		self.OnFocusObject(self.selectModels)

	def OnFocusObject(self,selected):
		self.destroyUI()

		if selected == None : return

		if len(selected) == 1 :
			self.selectModels = selected;
			self.buildComponentsUI(selected[0])

	def destroyUI(self):
		self.selectModels = None
		for i in range(0,self.ui_ToolBox.count()):
			widget = self.ui_ToolBox.widget(0)
			
			self.ui_ToolBox.removeItem(0)
			widget.deleteLater();

	   
	def buildComponentsUI(self,model):
		i=0
		for idx in model.componentIds:
			uic = ComponentController.COMPONENTSUI.get(idx,None)
			if uic : self.ui_ToolBox.addItem(uic(model,i,self.ui_ToolBox),idx)
			i+=1

	def uicall_AddComponent(self):
		if self.selectModels :
			addcom = AddComponent()
			select = addcom.exec_()

			for m in self.selectModels :
				ComponentController.getInstance().Add(m,select)

def start():
	dMain = DesignerMain()

	existBrowser   = hasattr(dMain,"browser") and dMain.browser
	existLayerList = hasattr(dMain,"layerList") and dMain.layerList
	if existBrowser and existLayerList:
		dMain.tabifyDockWidget(dMain.browser,dMain.layerList)

	property = PropertyDock(dMain)
	if hasattr(dMain,"_property") and dMain._property:
		dMain.removeDockWidget(dMain._property)
	dMain._property = property
	dMain.addDockWidget(QtCore.Qt.RightDockWidgetArea,property)