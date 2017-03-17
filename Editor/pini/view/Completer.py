# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from PySide.QtGui import * 
from PySide.QtCore import *
from view.ExplainWebView import ExplainWebView

class ListView(QListView):
	def __init__(self,completer,parent=None):
		super(ListView,self).__init__(parent)

		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.completer = completer

	def hideEvent(self,e):
		self.completer.closeExplain()
		super(ListView,self).hideEvent(e)

class Completer(QCompleter) : 
	# 자동완성창
	def __init__(self,parent=None):
		super(Completer,self).__init__(parent)

		self.prepare = False

		self.eventing = True

		self.previousRow = -1
		self.explains = []

		self.parent = parent
		self.explain = QFrame(parent,Qt.Popup)
		self.explain.setStyleSheet("QFrame{border:1px solid #666;border-radius:5px;}")

		self.explain_text = ExplainWebView(self,self.explain)
		self.explain_img = QLabel(self.explain)

		self.explain_img.resize(0,0)
		self.explain_text.resize(0,0)
		self.explain_text.move(2,2)

		self.setPopup(ListView(self))

	def complete(self,r,explains=[]):
		self.explains = explains
		self.previousRow = -1
		self.explain.resize(200,200)
		self.explain_text.resize(196,196)
		self.explain_img.setPixmap(QPixmap())

		x = r.x()+r.width()+2
		y = r.y()+r.height()
		pos = self.parent.mapToGlobal(QPoint(x,y))

		self.prepare = True

		self.explain.move(pos)
		self.explain.show()

		super(Completer,self).complete(r)

		self.prepare = False

	def closeExplain(self):
		if self.explain.isVisible():
			self.explain.close()
			self.explain_text.setHtml("")

	def event(self,ev):
		return super(Completer,self).event(ev)

	def eventFilter(self,o,e):
		if self.eventing == True:
			self.eventing = False
			if self.popup().isVisible() : 
				currentRow = self.popup().currentIndex().row()
				if currentRow != self.previousRow :
					if len(self.explains) > currentRow : 
						content = self.explains[currentRow]
						if content.startswith("img://"):
							self.explain_text.resize(0,0)
							self.explain_text.setHtml("")

							pix,size = GraphicsProtocolObject().LoadImg(content.replace("img://",""))
							pix = QPixmap.fromImage(pix).scaled(200,200)
							
							self.explain_img.resize(200,200)
							self.explain_img.setPixmap(pix)
						else:
							self.explain_text.resize(196,196)
							self.explain_text.setHtml(content)

							self.explain_img.resize(0,0)
							self.explain_img.setPixmap(QPixmap())
					else:
						self.explain_text.setHtml(u"설명이 없습니다.")
				self.previousRow = currentRow
			elif self.explain.isVisible() and self.prepare == False : 
				pass
			self.eventing = True

		return QCompleter.eventFilter(self,o,e)