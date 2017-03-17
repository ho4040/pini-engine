# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from PySide.QtGui import *
from PySide.QtCore import *
from Noriter.UI.ModalWindow import ModalWindow 
from Noriter.UI.Window import Window 
from Noriter.UI.Widget import Widget 
from Noriter.utils.Settings import Settings
from Noriter.views.NoriterMainWindow import * 

from controller.ProjectController import ProjectController
from controller.SceneListController import SceneListController
from view.ScriptEditor import ScriptEditor

class FindAllWindow(Window):
	def __init__(self,finder,word):
		self.finder = finder
		self.word = word

		super(FindAllWindow,self).__init__(None)
		self.setWindowTitle(u"모두 찾기 : "+word+u" ("+str(len(self.alls))+u"개 검색 됨)")

		self.list.doubleClicked.connect(self.selectFindElement)

	@LayoutGUI
	def GUI(self):
		self.alls = self.finder.findAll(self.word)
		self.list = self.Layout.listbox(self.findAllFactory,self.alls)
	
	def selectFindElement(self,idx):
		self.finder.textEdit.setTextCursor(self.alls[idx])
		self.finder.textEdit.setFocus()

	def findAllFactory(self,cur):
		self.Layout.label(str(cur.block().blockNumber()+1)+u" 라인").setStyleSheet("color:#e6db74;background-color:none")

		text = cur.block().text()
		start = cur.selectionStart() - cur.block().position()
		end = cur.selectionEnd() - cur.block().position()

		text1 = text[0:start].replace(">","&gt;").replace("<","&lt;")
		text2 = text[start:end].replace(">","&gt;").replace("<","&lt;")
		text3 = text[end:len(text)].replace(">","&gt;").replace("<","&lt;")

		text = text1+"<b><font color='red'>"+text2+"</font></b>"+text3

		self.Layout.label(text).setTextFormat(Qt.RichText)#.setStyleSheet("Text-align:left")
		self.Layout.hline()
		return 40

class FinderWidget(Widget):
	def __init__(self,textEdit,parent = None):
		super(FinderWidget,self).__init__(parent)
		self.GUI()

		self.textEdit = textEdit

	@LayoutGUI
	def GUI(self):
		with Layout.HBox(5) :
			self.Layout.label(u" 검색 :")
			self.find_text = self.Layout.input("",self.inputUpdate);
			self.find_button = self.Layout.button(u"검색",self.findNext);
			self.findAll_button = self.Layout.button(u"모두 검색",self.openFindAllWindow);

		self.replace_gap = self.Layout.gap(1)
		with Layout.HBox(5) :
			self.replace_label=self.Layout.label(u" 대치 :")
			self.replace_text = self.Layout.input("",None);
			self.replace_button = self.Layout.button(u"대치",self.replaceNext);
			self.replaceAll_button = self.Layout.button(u"모두 대치",self.runReplaceAll);

		self.replaceAll_button.setFixedHeight(20)
		self.replace_button.setFixedHeight(20)
		self.findAll_button.setFixedHeight(20)
		self.find_button.setFixedHeight(20)

	def showFind(self):
		self.show()
		self.replace_gap.hide()
		self.replace_label.hide()
		self.replace_text.hide()
		self.replace_button.hide()
		self.replaceAll_button.hide()

	def showReplace(self):
		self.show()
		self.replace_gap.show()
		self.replace_label.show()
		self.replace_text.show()
		self.replace_button.show()
		self.replaceAll_button.show()


	def showEvent(self,event):
		super(FinderWidget,self).showEvent(event)
		self.find_text.setFocus()
		self.find_text.selectAll()

	def hideEvent(self,event):
		super(FinderWidget,self).hideEvent(event)
		self.textEdit.setFocus()

	def keyPressEvent(self,event):
		super(FinderWidget,self).keyPressEvent(event)
		if event.key() == Qt.Key_Escape : 
			self.hide()

		if event.key() in [Qt.Key_Enter,Qt.Key_Return] : 
			if QApplication.focusWidget() == self.find_text : 
				self.findNext()
			elif QApplication.focusWidget() == self.replace_text :
				self.replaceNext()

	def findAll(self,word):
		tc = self.textEdit.textCursor()
		self.textEdit.moveCursor(QTextCursor.Start);

		alls = [] 
		while True :
			if self.textEdit.find(word):
				cur = self.textEdit.textCursor()
				alls.append(cur)
			else:
				break;
		self.textEdit.setTextCursor(tc)
		return alls

	def replaceAll(self,find,replace):
		alls = self.findAll(find)
		btn = QMessageBox.question(self, u"피니엔진", 
										 find+u"(을/를) "+replace+u"로 대치하시겠습니까?\n총 "+str(len(alls))+"개",
								   		 QMessageBox.Yes , QMessageBox.No )
		
		if btn == QMessageBox.Yes : 
			for cur in alls : 
				self.textEdit.setTextCursor(cur)
				cur.insertText(replace)

	def runReplaceAll(self):
		self.replaceAll(self.find_text.text(),self.replace_text.text())

	def openFindAllWindow(self):
		FindAllWindow(self,self.find_text.text())

	def findNext(self):
		search = self.textEdit.find(self.find_text.text())
		if search == False : 
			tc = self.textEdit.textCursor()
			self.textEdit.moveCursor(QTextCursor.Start);
			search = self.textEdit.find(self.find_text.text());
			if search == False :
				self.textEdit.setTextCursor(tc)
				return False
		return True

	def replaceNext(self):
		if self.inputUpdate() : 
			length = len(self.replace_text.text())
			tc = self.textEdit.textCursor()
			tc.insertText(self.replace_text.text())
			tc.movePosition(QTextCursor.Left,QTextCursor.MoveAnchor,length)
			tc.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor,length)
			self.textEdit.setTextCursor(tc)
		else:
			pass#alert!!! not find!

	def inputUpdate(self):
		tc = self.textEdit.textCursor()
		length = len(tc.selectedText())
		tc.clearSelection();

		tc.movePosition(QTextCursor.Left,QTextCursor.MoveAnchor,length)
		self.textEdit.setTextCursor(tc)
		return self.findNext()

class SceneScriptWindowManager(object):
	_instance = None
	_isInit   = False
	def __new__(cls, *args, **kwargs):
		if not SceneScriptWindowManager._instance:
			SceneScriptWindowManager._instance = super(SceneScriptWindowManager,cls).__new__(cls,*args,**kwargs)

		return SceneScriptWindowManager._instance

	def __init__(self):
		self.windows = {}
		self.activateQueue = []
		self.active = None
		print "9_2_2"
		self.sceneListCtrl = SceneListController.getInstance()
		print "9_2_3"
		self.sceneListCtrl.SceneOpen.connect(self.openScene)
		print "9_2_4"

	def openScene(self,sceneCtrl):
		curDir = QDir(ProjectController().path)
		curDir = curDir.relativeFilePath(sceneCtrl.path)
		if curDir in self.windows : 
			self.windows[curDir].raise_()
			self.windows[curDir].editor.setFocus()
		else:
			self.windows[curDir] = SceneScriptWindow()
			self.activateQueue.append(self.windows[curDir])
			self.windows[curDir].openScene(curDir,sceneCtrl)
			m = NoriterMain()
			m.Dock(NoriterMain.DOCK_RIGHT,self.windows[curDir],True)
			self.setActive(self.windows[curDir])
			self.windows[curDir].editor.setFocus()

	def saveActiveScene(self):
		if self.active != None:
			self.active.saveScene()

	def saveAll(self):
		for k,v in self.windows.iteritems():
			v.editor.saveScene()

	@staticmethod
	def getInstance():
		return SceneScriptWindowManager._instance

	def getActive(self):
		return self.active

	def getActiveFilename(self):
		if self.active != None:
			return self.active.fileName
		return None

	def setActive(self,view):
		self.active = view
		self.activateQueue.remove(view)
		self.activateQueue.append(view)

	def remove(self,idx):
		if idx in self.windows : 
			self.activateQueue.remove(self.windows[idx])
			del self.windows[idx]

			if len(self.activateQueue) > 0:
				self.activateQueue[-1].editor.setFocus()
			else:
				self.active = None
				ProjectController().workerController.terminate()

	def reset(self):
		for k in self.windows.keys():
			result = self.windows[k].close()

			if not result:
				return False

		self.windows = {}
		self.activateQueue = []
		self.active = None

		return True

class SceneScriptWindow(Window):
	def __init__(self,parent=None):
		print "9_2_0"
		super(SceneScriptWindow,self).__init__(parent)
		print "9_2_1"
		self.setWindowTitle(u"LNX 스크립트")
		self.fileName = u""
		print "9_2_6"
		self.setFeatures(QtGui.QDockWidget.DockWidgetClosable | QtGui.QDockWidget.DockWidgetFloatable | QtGui.QDockWidget.DockWidgetMovable)
		print "9_2_7"
		self.show()
		print "9_2_8"

	@LayoutGUI
	def GUI(self):
		self.editor = self.Layout.addWidget(ScriptEditor(self,self))

		self.text = self.Layout.addWidget(FinderWidget(self.editor,self));
		self.text.hide();

	def closeEvent(self,event):
		if self.editor.NeedSaveActivate() == 0:
			event.ignore()
			return

		SceneScriptWindowManager.getInstance().remove(self.fileName)

		super(SceneScriptWindow,self).closeEvent(event)

	def keyPressEvent(self,event):
		super(SceneScriptWindow,self).keyPressEvent(event)
		if event.modifiers() == Qt.ControlModifier :
			if event.key() == 70 : 
				showFind()
			elif event.key() == 72 :
				showReplace()

	def focusEnabled(self):
		SceneScriptWindowManager.getInstance().setActive(self)

	def focusDisabled(self):
		pass

	def setNeedSaveStatus(self,needSave):
		if needSave:
			self.setWindowTitle(self.fileName + u"*")
		else:
			self.setWindowTitle(self.fileName)

	def showFind(self):
		self.text.hide()
		self.text.showFind()
		self.editor.Ctrl = None

	def showReplace(self):
		self.text.hide()
		self.text.showReplace()
		self.editor.Ctrl = None

	def openScene(self,curDir,sceneCtrl):
		self.fileName = curDir
		self.setWindowTitle(curDir)
		self.editor.openScene(sceneCtrl)

	def saveScene(self):
		self.editor.saveScene()

	def loadScene(self,path):
		pass

