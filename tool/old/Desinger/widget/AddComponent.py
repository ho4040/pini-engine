from PySide.QtGui import * 
from PySide.QtCore import * 

from uic.Ui_AddComponent import *
from controller.ComponentController import *

class AddComponent(QDialog,Ui_AddComponent):
	def __init__(self,parent=None):
		super(AddComponent,self).__init__(parent)
		self.setupUi(self)

		self._apply = False

		#connect
		self.ui_add.clicked.connect(self.uicall_add)

		i=0
		for key,value in ComponentController.COMPONENTSUI.iteritems():
			self.ui_Edit.insertItem(i,key)
			i+=1

		self.ui_Edit.setInsertPolicy(QComboBox.NoInsert)

	def uicall_add(self):
		text = self.ui_Edit.currentText()
		idx = self.ui_Edit.findText(text)
		if idx >= 0:
			self._apply = True
			self.close()

	def exec_(self):
		super(AddComponent,self).exec_()

		if self._apply :
			return self.ui_Edit.currentText()

		return ""

