from PySide import QtCore,QtGui

class TabWidget(QtGui.QTabWidget):
	class __tab__(object):
		def __init__(self,tabbar,text):
			from Noriter.UI.Layout import Layout

			self.tabbar = tabbar
			self.widget = QtGui.QWidget(self.tabbar)
			self.Layout = Layout.getInstance()

			self.tabbar.addTab(self.widget,text)

		def __enter__(self):
			self.layout = self.Layout.OnWidget(self.widget)
			return self

		def __exit__(self, exc_type, exc_val, exc_tb):
			self.Layout.End(self.layout)

	def __init__(self,parent=None):
		super(TabWidget,self).__init__(parent)
		
		from Noriter.UI.Layout import Layout
		self.Layout = Layout.getInstance()
		self.GUI()

	def GUI(self):
		pass

	def tab(self,title):
		return TabWidget.__tab__(self,unicode(title))

	def focus(self,idx):
		self.setCurrentIndex(idx)