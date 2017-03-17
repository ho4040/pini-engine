from PySide import QtCore,QtGui

class Splitter(QtGui.QSplitter):
	class __split__(object):
		def __init__(self,split):
			from Noriter.UI.Layout import Layout

			self.split = split
			self.widget = QtGui.QWidget(self.split)
			self.Layout = Layout.getInstance()

			self.split.addWidget(self.widget)

		def __enter__(self):
			self.layout = self.Layout.OnWidget(self.widget)
			return self

		def __exit__(self, exc_type, exc_val, exc_tb):
			self.Layout.End(self.layout)

	def __init__(self,parent=None):
		super(Splitter,self).__init__(parent)
		
		from Noriter.UI.Layout import Layout
		self.Layout = Layout.getInstance()
		self.GUI()

	def GUI(self):
		pass

	def split(self):
		return Splitter.__split__(self)

	def focus(self,idx):
		pass #self.setCurrentIndex(idx)