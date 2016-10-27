# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from PySide.QtGui import * 
from PySide.QtCore import *
from PySide.QtWebKit import *

class ExplainWebView(QWebView) : 
	# 자동완성과 같이 뜨는 툴팁창
	def __init__(self,completer,parent=None):
		super(ExplainWebView,self).__init__(parent)
		self.completer = completer
		self.loadFinished.connect(self.onLoadFinished)
		self.linkClicked.connect(self.onLinkClicked)

		self.settings().setUserStyleSheetUrl(QUrl.fromLocalFile("resource/explain.css"));

	def onLoadFinished(self,ok):
		self.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)

	def onLinkClicked(self,url):
		QDesktopServices.openUrl(url);

	def hideEvent(self,e):
		self.clearFocus()
		return super(ExplainWebView,self).hideEvent(e)