# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from PySide.QtGui import * 
from PySide.QtCore import *
from PySide.QtWebKit import *

class ExplainHoverWebView(QWebView) :
	# 마우스를 글자에 두었을때 뜨는 툴팁창
	def __init__(self,parent=None):
		super(ExplainHoverWebView,self).__init__(parent)
		self.loadFinished.connect(self.onLoadFinished)
		self.linkClicked.connect(self.onLinkClicked)

		self.settings().setUserStyleSheetUrl(QUrl.fromLocalFile("resource/explain.css"));

	def onLoadFinished(self,ok):
		self.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)

	def onLinkClicked(self,url):
		QDesktopServices.openUrl(url);

	def leaveEvent(self,e):
		self.resize(0,0)
		return super(ExplainHoverWebView,self).leaveEvent(e)

	def hideEvent(self,e):
		self.clearFocus()
		return super(ExplainHoverWebView,self).hideEvent(e)
