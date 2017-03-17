from Noriter.UI.Layout import *

class NoriterWindow(object):
	def __init__(self,parent=None):
		super(NoriterWindow,self).__init__(parent)

		self._layout = None
		self.Layout = Layout.getInstance()
		self.GUI()