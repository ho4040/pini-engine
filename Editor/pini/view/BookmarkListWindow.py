# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from Noriter.UI.Layout import *
from Noriter.UI.Window import Window
from Noriter.views.NoriterMainWindow import * 

from view.SceneScriptWindow import SceneScriptWindowManager

from controller.SceneListController import SceneListController
from controller.ProjectController import ProjectController

import json

class BookmarkListWindow(Window):
	_instance = None
	_isInit   = False
	def __new__(cls, *args, **kwargs):
		if not BookmarkListWindow._instance:
			BookmarkListWindow._instance = super(BookmarkListWindow,cls).__new__(cls,*args,**kwargs)

		return BookmarkListWindow._instance

	def __init__(self):
		if BookmarkListWindow._isInit:
			return 

		self.bookmarkMap = {}
		BookmarkListWindow._isInit = True
		super(BookmarkListWindow,self).__init__(NoriterMain())
		self.setWindowTitle(u"북마크 목록 뷰어")
		self.resize(400,300)

	@LayoutGUI
	def GUI(self):
		self.Layout.clear()

		self.tab = self.Layout.tab()
		self.tab.currentChanged.connect(self.tabSelChanged)

		if len(self.bookmarkMap.items()) > 0:
			self.tabSelected = self.bookmarkMap.items()[0]
		else:
			self.tabSelected = None

		for fileName, bookmarks in self.bookmarkMap.iteritems():
			with self.tab.tab(fileName) : 
				with Layout.VBox():
					self.bookmarkListBox = self.Layout.listbox(self.bookmarkListFactory, bookmarks)
					self.bookmarkListBox.clicked.connect(self.bookmarkSelChanged)
					# for bookmark in bookmarks:
					# 	bookmarkLabel = self.Layout.label(bookmark)
			
	def tabSelChanged(self,idx):
		if self.tabSelected != None:
			self.tabSelected = self.bookmarkMap.items()[idx]
		pass

	def bookmarkSelChanged(self,idx):

		path = ProjectController().path + "/scene/" + self.tabSelected[0].replace(".obj",".lnx")
		SceneListController.getInstance().Open(path)

		def ___():
			SceneScriptWindowManager.getInstance().getActive().editor.moveToLineNumber(self.tabSelected[1][idx]["line"])
			SceneScriptWindowManager.getInstance().getActive().editor.setFocus()

		QTimer.singleShot(30, ___)

	def bookmarkListFactory(self,data):
		bookmark = self.Layout.label(data["name"])
		return 25

	def parseObj(self,obj):
		bookmarks = []

		bookmarks.append({"name":u"#진입","line":0})

		for v in obj : 
			if v["t"] == 6 : # 매크로
				for z in v["stmts"]:
					if z["t"] == 3 : # 북마크
						book = z["name"][0]
						if book != "%": # if 문 관련 컴파일러 삽입 북마크는 무시합니다
							bookmarks.append({"name":z["name"],"line":z["ln"]})
					
			elif v["t"] == 3 : # 북마크
				book = v["name"][0]
				if book != "%": # if 문 관련 컴파일러 삽입 북마크는 무시합니다
					bookmarks.append({"name":v["name"],"line":v["ln"]})

		return bookmarks

	def refreshData(self):
		# self.view.clearObj()

		self.objMap = {}
		PROJPATH = ProjectController().path
		OBJECTPATH = (PROJPATH + "/build/obj/").replace("\\","/")
		for root, dirs, files in os.walk(OBJECTPATH, topdown=False):
			for name in files:
				fullpath = os.path.join(root, name).replace("\\","/")
				if fullpath.find("libdef") == -1:
					idx =  fullpath.replace(OBJECTPATH+"scene/","")

					fp = QFile(fullpath)
					fp.open(QIODevice.ReadOnly | QIODevice.Text)

					fin = QTextStream(fp)
					fin.setCodec("UTF-8")

					obj = json.loads(fin.readAll())

					fin = None
					fp.close()

					self.bookmarkMap[idx] = self.parseObj(obj)

		self.GUI()

		####build!
		# for k,v in self.objMap.iteritems():
		# 	self.view.addObj( k.replace(".obj","") , v )


