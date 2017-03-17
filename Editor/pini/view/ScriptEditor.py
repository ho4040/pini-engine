# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from PySide.QtGui import * 
from PySide.QtCore import *

from Noriter.UI.ModalWindow import ModalWindow 
from Noriter.UI.Window import Window 
from Noriter.utils.Settings import Settings
from Noriter.views.NoriterMainWindow import * 

from view.VariableViewWindow import VariableViewWindow
from view.ExplainHoverWebView import ExplainHoverWebView
from view.ExplainWebView import ExplainWebView
from view.Completer import Completer
from view.Highlighter import Highlighter

from command.CompileThread import *
from command.FontManager import FontManager
from command.ScriptCommands import ScriptCommand
from command.ScriptCommands import ScriptMarkup
from command.ScriptCommands import ScriptGraphicsProtocol
from command.ScriptCommands import GraphicsProtocolObject
from controller.SceneListController import SceneListController
from controller.ProjectController import ProjectController

import re
import threading

import math
import random
import time
from prof import Prof

import traceback

from compiler import LNXOptimizer
from view.OutputWindow import OutputWindow

class ScriptEditor(QPlainTextEdit):
	def sizeHint(self):
		return QtCore.QSize(600, 2000)

	class LineNumberArea(QWidget):
		# 줄 번호 표기
		def __init__(self,parent):
			super(ScriptEditor.LineNumberArea,self).__init__(parent) 
			self.editor = parent
			self.update()

		def sizeHint(self):
			return QSize(self.editor.lineNumberAreaWidth(), 0)

		def paintEvent(self,event):
			super(ScriptEditor.LineNumberArea,self).paintEvent(event) 
			self.editor.lineNumberAreaPaintEvent(event)

		def getLineNumberFromYPos(self,ypos):
			block = self.editor.firstVisibleBlock()
			blockNumber = block.blockNumber()

			top = int(self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top())
			height = int(self.editor.blockBoundingRect(block).height())

			lineNumber = (ypos-top) / height + blockNumber
			if lineNumber < 0:
				lineNumber = 0
			return lineNumber

		def mousePressEvent(self,event):
			blockNumber = self.getLineNumberFromYPos(event.y())

			tc = self.editor.textCursor()
			tc.movePosition(QTextCursor.Start)
			tc.movePosition(QTextCursor.NextBlock,QTextCursor.MoveAnchor,blockNumber)
			tc.movePosition(QTextCursor.EndOfBlock,QTextCursor.KeepAnchor)

			self.pressedBlockNumber = blockNumber

			self.editor.setTextCursor(tc)

		def mouseMoveEvent(self,event):
			blockNumber = self.getLineNumberFromYPos(event.y())

			startBlockNumber = self.pressedBlockNumber
			endBlockNumber = blockNumber

			tc = self.editor.textCursor()
			if startBlockNumber <= endBlockNumber:
				tc.movePosition(QTextCursor.Start)
				tc.movePosition(QTextCursor.NextBlock,QTextCursor.MoveAnchor,startBlockNumber)
				tc.movePosition(QTextCursor.NextBlock,QTextCursor.KeepAnchor,endBlockNumber-startBlockNumber)
				tc.movePosition(QTextCursor.EndOfBlock,QTextCursor.KeepAnchor)
			else:
				tc.movePosition(QTextCursor.Start)
				tc.movePosition(QTextCursor.NextBlock,QTextCursor.MoveAnchor,startBlockNumber)
				tc.movePosition(QTextCursor.EndOfBlock,QTextCursor.MoveAnchor)
				tc.movePosition(QTextCursor.PreviousBlock,QTextCursor.KeepAnchor,startBlockNumber-endBlockNumber)

			self.editor.setTextCursor(tc)

		def mouseReleaseEvent(self,event):
			pass

		def wheelEvent(self,event):
			self.editor.wheelEvent(event)

	def __init__(self,sceneScriptWindow,parent=None):
		super(ScriptEditor,self).__init__(parent)
		self.sceneScriptWindow = sceneScriptWindow

		self.setWindowTitle(u"스크립트 에디터")
		self.compiledCommand=[]
		self.compiledCommand.append(self.compiledText(''))

		self.mouseHoveringTimer = QTimer(self)
		self.mouseHoveringTimer.timeout.connect(self.mouseHoveringTick)
		self.mouseHoveringTimer.start(500)
		self.mouseHoveringCounter = -1 # 시작시에는 발동하지 않습니다
		self.mouseHoveringCloseDistance = -1
		self.setMouseTracking(True)

		self.bookmarks = []

		self.prevBlockCount = 1

		self.EnterIgnore = False
		self.previewUpdate = False
		self.previewBlockNumber = 0

		self.errorLineTimer = QTimer(self)
		self.errorLineTimer.timeout.connect(self.updateErrorLine)
		self.errorLineTimer.start(1000)

		self.linkStroker = None
		self.linkStrokerDashes = None
		self.sceneCtrl = None
		self.semiIdx = 1
		self.blockIdx = 1

		self.linkerLineTimer = QTimer(self)
		self.linkerLineTimer.timeout.connect(self.updateBlockLinkStroker)
		self.linkerLineTimer.start(50)

		self.tempSaveFin = 0
		self.tempSaveTimer = QTimer(self)
		self.tempSaveTimer.timeout.connect(self.tempSave)

		self.updateBlockLinkStroker()

		self.noCommmandAdd = None
		self.pressKey = None
		self.completionCallback = None
		self.lineNumber = self.LineNumberArea(self)

		self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
		self.updateRequest.connect(self.updateLineNumberArea)

		self.updateLineNumberAreaWidth(0)

		self.setWordWrapMode(QTextOption.NoWrap)

		self.markups = QStringListModel(ScriptMarkup.Markup())

		self.completer = Completer(self)
		self.completer.setCaseSensitivity(Qt.CaseInsensitive)
		self.completer.setWrapAround(False)
		self.completer.activated.connect(self.insertCompletion)
		self.completer.setWidget(self)
		self.completer.setCompletionMode(QCompleter.PopupCompletion)
		self.document().cursorPositionChanged.connect(self.cursorPositionChanged)
		self.document().contentsChange.connect(self.scriptChanged)
		self.highlighter = Highlighter(self.document())

		self.explainHoverWebView = ExplainHoverWebView(self)
		self.explainHoverWebView.setWindowFlags(Qt.Window | Qt.ToolTip)
		self.explainHoverWebView.resize(0,0)

		self.setCursorWidth(2)

		self.compilingThread = CompilingThread(self,self)
		self.compilingThread.beginBusy.connect(self.OnCompilingThreadBeginBusy)
		self.compilingThread.completeCallback.connect(self.OnCompilingThreadCallback)

		family = FontManager().FontName("NanumGothicCoding")

		fnt = self.font()
		fnt.setPointSize(11)
		fnt.setFamily(family)
		fnt.setFixedPitch(True)
		self.setFont(fnt)

		fntfm = self.currentCharFormat()
		fntfm.setForeground(QColor(247,248,232))
		self.setCurrentCharFormat(fntfm)

		self.setTabStopWidth(4*self.fontMetrics().width(' '));
		self.fontSizeAnim = 0

		m = NoriterMain()
		try:
			m.closeSignal.disconnect(self.mainWindowClose)
		except Exception, e:
			pass
		m.closeSignal.connect(self.mainWindowClose)

	def NeedSaveActivate(self):
		from view import Menu
		if self.sceneCtrl and self.sceneCtrl.needSave : 
			self.sceneScriptWindow.focusEnabled()
			if Menu.Save(True,True) == 0 : 
				return 0

			self.sceneCtrl.needSave = False
			self.sceneScriptWindow.close()

		targetPath = self.getTempFileName()
		PROJPATH = ProjectController().path

		tempDir = "tempSave"
		fp = None
		tmp_path_1 = os.path.join(".",tempDir,targetPath)

		if os.path.exists(tmp_path_1):
			os.remove(tmp_path_1)

		return 1

	def mainWindowClose(self,main,event):
		result = self.NeedSaveActivate()

		if result == 0:
			event.ignore()
			return

		tempDir = "tempSave"
		for root, dirs, files in os.walk(os.path.join(".",tempDir), topdown=False):
			if len(files) == 1:
				if files[0] == "PROJ":
					os.remove(os.path.join(".",tempDir,"PROJ"))
					os.rmdir(os.path.join(".",tempDir))

	def showEvent(self,event):
		self.compilingThread.start()

	def hideEvent(self,event):
		self.compilingThread.doDestroy()
		self.compilingThread.wait()		

	def openScene(self,sceneCtrl):
		self.sceneCtrl = sceneCtrl
		self.setPlainText(sceneCtrl.plainText)
		self.compileAll()
		self.commitGraphics()
		self.sceneCtrl.needSave = False
		self.sceneScriptWindow.setNeedSaveStatus(False)

	def setPlainText(self,text):
		self.noCommmandAdd = True
		super(ScriptEditor,self).setPlainText(text)
		self.noCommmandAdd = None

	def saveScene(self):
		self.sceneCtrl.Save(self.toPlainText())
		self.sceneScriptWindow.setNeedSaveStatus(False)
		ProjectController().compileProj()

	def cursorPositionChanged(self,cursor):
		self.updateLine()
		self.commitGraphics()
	
	def selectedCommand(self,text,tc):
		tc.movePosition(QTextCursor.Left)
		tc.select(QTextCursor.WordUnderCursor)

		if tc.selectedText()[-1] == "[":
			tc.clearSelection()

		if tc.selectedText()[-2:] == "[]":
			tc.clearSelection()
			tc.movePosition(QTextCursor.Left)

		tc.insertText(text)
		ScriptCommand.Selected(self,text,tc)

	def completionClose(self):
		self.completer.popup().hide()

	def completionShow(self,model,callback=None,explains=[]):
		if model.rowCount() == 0 :
			return

		self.completionCallback = callback
		self.completer.setModel(model)
		r = self.cursorRect()
		p = self.completer.popup()
		r.setWidth(p.sizeHintForColumn(0)+p.verticalScrollBar().sizeHint().width());
		self.completer.complete(r,explains)

	def focusInEvent(self,event):
		super(ScriptEditor,self).focusInEvent(event)
		self.sceneScriptWindow.focusEnabled()

	def focusOutEvent(self,event):
		super(ScriptEditor,self).focusOutEvent(event)
		self.sceneScriptWindow.focusDisabled()

	def mousePressEvent(self,event):
		super(ScriptEditor,self).mousePressEvent(event)
		self.cursorPositionChanged(self.textCursor())

	def mouseMoveEvent(self,event):
		if self.mouseHoveringCloseDistance >= 0:
			dx = self.xCoor - event.x()
			dy = self.yCoor - event.y()
			self.mouseHoveringCloseDistance += dx * dx + dy * dy

			if self.mouseHoveringCloseDistance > 100:
				self.mouseHoveringCloseDistance = -1
				self.explainHoverWebView.resize(0,0)

		self.xCoor = event.x()
		self.yCoor = event.y()
		self.mouseHoveringCounter = 0
		super(ScriptEditor,self).mouseMoveEvent(event)

	def leaveEvent(self,event):
		self.mouseHoveringCounter = -1 # 마우스가 편집창에서 떠나면, 작동하지 않습니다.
		super(ScriptEditor,self).leaveEvent(event)

	def moveToLineNumber(self,lineNo):
		tc = self.textCursor()
		tc.movePosition(QTextCursor.Start)
		tc.movePosition(QTextCursor.NextBlock,QTextCursor.MoveAnchor,lineNo)
		tc.movePosition(QTextCursor.EndOfBlock,QTextCursor.KeepAnchor)
		self.setTextCursor(tc)

	def mouseHoveringTick(self):
		if self.mouseHoveringCounter < 0:
			return

		self.mouseHoveringCounter = self.mouseHoveringCounter + 1

		if self.mouseHoveringCounter == 3: # 1.5초동안 가만히 있으면 작동합니다
			block = self.firstVisibleBlock()
			blockNumber = block.blockNumber()

			top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
			height = int(self.blockBoundingRect(block).height())

			lineNumber = (self.yCoor-top) / height + blockNumber

			if lineNumber < 0:
				lineNumber = 0

			tc = self.textCursor()
			tc.movePosition(QTextCursor.Start)
			tc.movePosition(QTextCursor.NextBlock,QTextCursor.MoveAnchor,lineNumber)

			while 1:
				if lineNumber != tc.blockNumber():
					break
				if tc.atEnd():
					break

				tc.movePosition(QTextCursor.Right)
				if self.xCoor < self.cursorRect(tc).left():
					tc.movePosition(QTextCursor.Left)
					tc.select(QTextCursor.WordUnderCursor)
					self.explainHoverWebView.move(self.mapToGlobal(QPoint(self.xCoor+10,self.yCoor+10)))
					self.mouseHoveringCloseDistance = 0

					arg,argpos = self.currentArgument(tc)
					cmd,pos = self.currentCommand(tc)

					explain = ScriptCommand.GetExplainArg(cmd,arg)

					if explain == None:
						explain = ScriptCommand.GetExplainArg(cmd,tc.selectedText())
					if explain == None:
						explain = ScriptCommand.GetExplain(cmd)

					if explain != None:
						self.explainHoverWebView.resize(196,196)
						self.explainHoverWebView.show()
						self.explainHoverWebView.setHtml(explain)

					break

	def insertCompletion(self,completion):
		if self.completer.widget() is not self:
			return

		tc = self.textCursor()

		self.EnterIgnore = True

		callback = self.completionCallback
		self.completionCallback = None
		qApp.inputContext().reset()

		def ___():
			if callback :
				callback(completion,tc)
			else:
				tc.insertText(completion)
			
				cmd,pos = self.currentCommand()
				self.nextArg(cmd,pos)

		QTimer.singleShot(50, ___)
		QTimer.singleShot(100, self.__EnterIgnore)

	def __EnterIgnore(self):
		self.EnterIgnore = False
		
	def textUnderCursor(self):
		tc = self.textCursor()
		tc.select(QTextCursor.WordUnderCursor)
		return tc.selectedText()

	def updateLine(self):
		self.commandUpdate(self.textCursor().blockNumber())
		self.update()

	def findGoto(self,bookmark):
		a = []
		for i in range(0,self.blockCount()):
			try:
				c = self.compiledCommand[i] # 컴파일 중일 경우, 실패할 수도 있다
				if c and c["goto"] == bookmark:
					a.append(i)
			except Exception, e:
				pass
		return a

	def bookmarkList(self):
		if len(self.bookmarks) == 0 :
			for i in range(self.blockCount()-1,-1,-1):
				c = self.compiledCommand[i]
				if c and c["bookmark"] :
					if not c["bookmark"] in self.bookmarks and c["bookmark"][0] != "%":
						self.bookmarks.append(c["bookmark"])
		return self.bookmarks

	def findBookmark(self,name):
		try:
			for i in range(self.blockCount()-1,-1,-1):
				c = self.compiledCommand[i]
				if c and c["bookmark"] == name : 
					return i
		except Exception, e:
			return None

	def updateBlockLinkStroker(self):
		if self.linkStroker == None : 
			self.linkStrokerCount1 = 10
			self.linkStrokerCount2 = 10
			self.linkStroker = QPainterPathStroker()
			self.linkStroker.setWidth(3);
			self.linkStrokerDashes = [
				10,10,
				10,10,
				10,10,
				10,10,
				10,10
			]

		update = False
		blockNum = self.textCursor().blockNumber()
		try:
			c = self.compiledCommand[blockNum]
			if c and c["bookmark"] or c["goto"]:
				update = True

			if update:
				self.linkStrokerDashes[0] = self.linkStrokerCount2;
				self.linkStrokerDashes[1] = self.linkStrokerCount1;
				self.linkStrokerCount1 -= 1
				self.linkStrokerCount2 -= 1
				if self.linkStrokerCount1 < 0 : 
					if self.linkStrokerCount2 < 0 : 
						self.linkStrokerCount2 = 9
						self.linkStrokerCount1 = 9

				self.linkStroker.setDashPattern(self.linkStrokerDashes)
				self.update()

		except Exception, e:
			pass
		
	def blockLinkPaint(self,painter,booked,goto):
		yheight = 20
		if booked > goto : 
			yheight = -20

		b1 = self.document().findBlockByLineNumber(booked)
		b2 = self.document().findBlockByLineNumber(goto)

		geo1 = self.blockBoundingGeometry(b1)
		geo2 = self.blockBoundingGeometry(b2)

		w2 = self.fontMetrics().boundingRect(b2.text().replace("\t","")).width()+90#*1.6#+50
		if w2 > self.width():
			w2 = self.width()
		ygap = 3

		s1 = QPoint(geo1.width()-20, geo1.y() + geo1.height()/2 + ygap)
		s2 = QPoint(w2-20, geo2.y() - yheight + geo2.height()/2 + ygap)
		s3 = QPoint(w2-40, geo2.y() + geo2.height()/2 + ygap)
		s4 = QPoint(w2-60, geo2.y() + geo2.height()/2 + ygap)

		path = QPainterPath()
		path.moveTo(s1)
		path.lineTo(s1)
		path.cubicTo(s2,s3,s4)
		
		p = painter.pen()
		
		pen = painter.pen()
		pen.setStyle(Qt.DotLine);
		pen.setColor(QColor(255,255,255,122))
		painter.setPen(pen)

		ygap = 5
		painter.drawLine(0,geo2.y(),w2,geo2.y())
		painter.drawLine(0,geo2.y()+geo2.height()+ygap,w2,geo2.y()+geo2.height()+ygap)
		painter.setPen(p)

		stroke = self.linkStroker.createStroke(path);
		painter.fillPath(stroke, QColor((goto*10)%122+122,(goto*5)%122+122,(goto*30)%122+122));
		#painter.drawPath(path)

		b = painter.brush()
		painter.setBrush(QBrush(QColor(226,70,45)));
		painter.drawEllipse ( s1, 5,5 )

		painter.setBrush(QBrush(QColor(152,226,45)));
		painter.drawEllipse ( s4, 5,5 )

		painter.setBrush(b);

	def tabVisualizingPaint(self,painter,event):
		block = self.firstVisibleBlock()

		pen = painter.pen()
		pen2 = painter.pen()
		pen.setStyle(Qt.SolidLine);
		pen.setColor(QColor(127,127,127,127))
		pen2.setStyle(Qt.DotLine);
		pen2.setColor(QColor(0,255,255,80))

		top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
		bottom = top + int(self.blockBoundingRect(block).height())

		while block.isValid() and block.isVisible():
			if top > event.rect().bottom():
				break
			if bottom >= event.rect().top():
				tc = QTextCursor(block)
				while not tc.atBlockEnd():
					rc = self.cursorRect(tc)
					tc.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor)
					rc2 = self.cursorRect(tc)

					if tc.selectedText() == "\t":
						painter.setPen(pen)
						painter.drawLine(rc.topLeft(),rc.bottomLeft())
						painter.setPen(pen2)
						painter.drawLine(rc.left(),(rc.top()+rc.bottom())/2,rc2.left(),(rc.top()+rc.bottom())/2)
					else:
						break

					tc.clearSelection()

			block = block.next()
			top = bottom
			bottom = top+int(self.blockBoundingRect(block).height())

	def paintEvent(self,e):
		#self.updateBlockLinkStroker()
		super(ScriptEditor,self).paintEvent(e)
		painter = QPainter(self.viewport())

		self.tabVisualizingPaint(painter,e)

		if e.rect ().height() > 100:
			painter.setRenderHint( QPainter.Antialiasing )
			painter.setFont(self.font())

			blockNum = self.textCursor().blockNumber()

			c = None

			if len(self.compiledCommand) > blockNum:
				c = self.compiledCommand[blockNum]

			if c :
				if c["bookmark"] : 
					a = self.findGoto(c["bookmark"])
					for p in a :
						self.blockLinkPaint(painter,blockNum,p)
				elif c["goto"] :
					a = self.findBookmark(c["goto"])
					if a is not None:
						self.blockLinkPaint(painter,a,blockNum)

		if self.fontSizeAnim > 0 : 
			ratio = self.fontSizeAnim / 1000.0

			viewRect = self.viewport().rect()
			painter.setPen( QPen(QColor(200,200,200,ratio*255)) )
			painter.setBrush( QBrush(QColor(70,70,70,ratio*120)) )
			painter.drawRoundedRect(QRect(viewRect.width()/2-50,viewRect.height()/2-30,100,60), 20.0, 20.0);
			
			fnt = QFont("arial",30)
			painter.setFont(fnt)
			size = self.font().pointSize()
			trect = painter.fontMetrics().width(str(size))
			painter.drawText(viewRect.width()/2-trect/2,viewRect.height()/2+15,str(size))

			self.fontSizeAnim -= 8 

			QTimer.singleShot(100,self.update)

	def markupCompletion(self,text,tc):
		tc.movePosition(QTextCursor.Left,QTextCursor.KeepAnchor)

		while tc.selectedText() != "<":
			tc.removeSelectedText()

			if tc.atBlockStart():
				break

			tc.movePosition(QTextCursor.Left,QTextCursor.KeepAnchor)

		tc.movePosition(QTextCursor.Right,QTextCursor.MoveAnchor)

		ScriptMarkup.MarkupCompletion(self,text,tc)

	def markupSuggestComplete(self,text,tc):
		s = self.findLine("\"",QTextDocument.FindBackward,tc)
		e = self.findLine("\"",None,tc)

		s.clearSelection()

		s.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor,e.position()-s.position() - 1)
		s.insertText(text)

	def functionSuggestCompletionShow(self):
		arg,argpos = self.currentArgument()
		cmd,pos = self.currentCommand()

		if (len(cmd) > 0) and (len(arg) > 0):
			return ScriptCommand.Step(self,cmd,arg)

		markup,markupPos = self.currentMarkup()

		if markup == u"연결":
			bmList = self.bookmarkList()

			if bmList != None:
				self.completionShow(QStringListModel(bmList),self.markupSuggestComplete)
				return True
		elif markup == u"폰트":
			fontList = []
			for k,v in FontManager().fonts.iteritems():
				if (k == "NanumGothicCoding"):
					continue
				fontList.append(k)

			if fontList:
				self.completionShow(QStringListModel(fontList),self.markupSuggestComplete)
				return True

		return False

	def functionArguCompletionShow(self):
		cmd,pos = self.currentCommand()

		if len(cmd) > 0:
			if cmd[-1] == "[":
				commands = ScriptCommand.List()
				self.completionShow(QStringListModel(commands[0]),self.selectedCommand,commands[1])
				return True

			blockNum = self.textCursor().blockNumber()
			c = self.compiledCommand[blockNum]["compiled"]
			
			_vars = []
			for v in c[1] : 
				if v["t"] == LNXOptimizer.cmd("call"): 
					break
				if v["t"] == LNXOptimizer.cmd("assign") : 
					ids = v["L"].split(".")
					if len(ids) >= 2 and ids[0] == cmd : 
						_vars.append(ids[1])

			extened,explain = ScriptCommand.CanInsertArgs(cmd,_vars)
			if extened :
				self.extensionCurrentCmd = cmd
				self.completionShow( QStringListModel(extened), self.ExtensionsComplete , explain )
				return True
		return False

	def ARG(self,name,args):
		if args == None:
			return ""

		new_ret = ""
		for v in args : 
			# new_ret += self._G(name+"."+v["l"]["v"]) +' = '+self.ASSIGN_R(v['r'])+"\n"
			new_ret += " " +v["l"]["v"]+"="+self.CALCULATE_PART(v["r"])

		return new_ret

	def _CALL(self,name,args):
		args = self.ARG(name,args)
		return "["+name+args+ "]"

	def _V(self,v):
		if v["t"] == 0:
			return v["v"]
		if v["t"] == 2:
			return '"'+v["v"]+'"'
		else:
			return str(v["v"])

	def CALCULATE_PART(self,v):
		ret = ""
		if isinstance(v["v"],tuple):
			ret = self.CALCULATE(v["v"][0],v["v"][2],v["v"][1])
		else:
			if "type" in v and v["type"] == "call_function" : 
				ret = self._CALL(v["name"]["v"],v["args"])
			else:
				ret = self._V(v)
		return ret

	def CALCULATE(self,L,R,OP):
		l = self.CALCULATE_PART(L)
		r = self.CALCULATE_PART(R)

		return l + OP + r

	def ExtensionsComplete(self,text,origTc):
		tc = QTextCursor(origTc)
		blckNumber = tc.blockNumber()
		intentCount = 0
		isQuoting = False
		# tc 의 위치가 쌍따옴표 밖인것은 보장됩니다.

		# 먼저, 스페이스바를 만날 때까지 뒤로 가면서 지워줍니다
		while 1:
			b1 = tc.blockNumber() != blckNumber
			b2 = tc.atStart()
			if b1 or b2 :
				break

			tc.clearSelection()
			tc.movePosition(QTextCursor.Left,QTextCursor.KeepAnchor)
			sel = tc.selectedText()

			if sel == " ":
				tc.removeSelectedText()
				break
			else:
				tc.removeSelectedText()

		# 그 다음, 스페이스바 정리를 합니다.

		tc2 = QTextCursor(origTc)

		# 먼저 [ 를 찾습니다. 다만, ] 가 나온다면, 나온 갯수만큼 [ 를 무시합니다.
		while 1:
			b1 = tc2.blockNumber() != blckNumber
			b2 = tc2.blockNumber() == 0 and tc2.position() == 0
			if b1 or b2 :
				break

			tc2.movePosition(QTextCursor.Left,QTextCursor.KeepAnchor)
			sel = tc2.selectedText()

			if isQuoting:
				if sel == "\"":
					isQuoting = not isQuoting
			else:
				if sel == "\"":
					isQuoting = not isQuoting
				elif sel == "[":
					if intentCount == 0 :
						tc2.clearSelection()
						break
					intentCount -= 1
				elif sel == "]":
					intentCount += 1

			tc2.clearSelection()

		# 다음, ] 를 찾습니다. 역시, [ 가 나온다면, 나온 갯수만큼 ] 를 무시합니다.
		intentCount = -1
		while 1:
			b1 = tc2.blockNumber() != blckNumber
			b2 = tc2.atBlockEnd()
			if b1 or b2 :
				break

			tc2.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor)
			sel = tc2.selectedText()[-1]

			if isQuoting:
				if sel == "\"":
					isQuoting = not isQuoting
			else:
				if sel == "\"":
					isQuoting = not isQuoting
				elif sel == "]":
					if intentCount == 0 :
						break
					intentCount -= 1
				elif sel == "[":
					intentCount += 1

		obj = ScriptCommand.GenObjLine(tc2.selectedText())

		if obj:
			rebuildMacro = "["
			rebuildMacro += obj[0]["name"]
			if obj[0]["args"] != None:
				for v in obj[0]["args"]:
					rebuildMacro += " "
					rebuildMacro += v["l"]["v"]
					rebuildMacro += "="
					rebuildMacro += self.CALCULATE_PART(v["r"])
			rebuildMacro += "]"

			tc2.insertText(rebuildMacro)

		tc = tc2
		tc.movePosition(QTextCursor.Left)

		tc.insertText(" "+text+"="+ScriptCommand.ArgDefault(self.extensionCurrentCmd,text))
		tc.clearSelection()
		tc.movePosition(QTextCursor.Left)
		self.setTextCursor(tc)
		self.functionSuggestCompletionShow()

	def BookmarkComplete(self,text,tc):
		# 블록 전체를 지운 뒤 다시 작성합니다
		indentCount = self.getIndent(tc.block().text())
		tc.movePosition(QTextCursor.StartOfBlock)
		tc.movePosition(QTextCursor.EndOfBlock,QTextCursor.KeepAnchor)
		tc.removeSelectedText()

		tc.insertText("\t"*indentCount)
		tc.insertText(">")
		self.setTextCursor(tc)
		self.insertText(text)

	def AnimationComplete(self,text,tc):
		tc.movePosition(QTextCursor.Left)
		tc.select(QTextCursor.WordUnderCursor)

		if tc.selectedText()[-1:] == "&":
			tc.clearSelection()

		tc.removeSelectedText()

		tc.insertText(text)

	def BlockComplete(self,text,origTc):
		tc = QTextCursor(origTc)
		tc.select(QTextCursor.LineUnderCursor)
		txt = tc.selectedText()
		tc.clearSelection()

		indent = self.getIndent(txt)

		def RemoveTypeChar(tc):
			# 먼저 @ 가 나올때까지 글자를 지웁니다
			blckNumber = tc.blockNumber()
			tc.clearSelection()

			while 1:
				b1 = tc.blockNumber() != blckNumber
				b2 = tc.blockNumber() == 0 and tc.position() == 0
				if b1 or b2 :
					break

				tc.movePosition(QTextCursor.Left,QTextCursor.KeepAnchor)
				sel = tc.selectedText()

				if sel == "@":
					tc.movePosition(QTextCursor.Right)
					break

				tc.removeSelectedText()

		if text == u"@매크로": 
			tab = u"\t"*(indent+1)
			tc.insertText(u"매크로 매크로명:\n"+tab+u"pass")
			tc.movePosition(QTextCursor.Left,QTextCursor.MoveAnchor,len(u"매크로 매크로명:\n"+tab+u"pass"))
			RemoveTypeChar(tc)
			tc.movePosition(QTextCursor.Right,QTextCursor.MoveAnchor,len(u"매크로 "))
			tc.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor,len(u"매크로명"))
			self.setTextCursor(tc)

		elif text == u"@조건" : 
			cc = u'''\
조건 2>1 :
(tab)	# 조건이 맞을 경우
(tab)	pass
(tab)@다른조건 3>1 :
(tab)	# 다른조건이 맞을 경우
(tab)	pass
(tab)@그외 : 
(tab)	# 모든 조건이 맞지 않을 경우
(tab)	pass
'''
			cc = cc.replace( u"(tab)", "\t"*indent )
			
			tc.insertText(cc)
			tc.movePosition(QTextCursor.Left,QTextCursor.MoveAnchor,len(cc))
			RemoveTypeChar(tc)
			tc.movePosition(QTextCursor.Right,QTextCursor.MoveAnchor,len(u"조건 "))
			tc.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor,len(u"2>1"))
			self.setTextCursor(tc)
		elif text == u"@애니메이션" : 
			cc = u'''\
애니메이션 애니메이션이름 :
(tab)	@노드 1:
(tab)		@프레임 0:
(tab)			&위치X 0
(tab)			&위치Y 0
(tab)		@프레임 10:
(tab)			&위치X 100
(tab)			&위치Y 100
'''
			cc = cc.replace( u"(tab)", "\t"*indent )
			
			tc.insertText(cc)
			tc.movePosition(QTextCursor.Left,QTextCursor.MoveAnchor,len(cc))
			RemoveTypeChar(tc)
			tc.movePosition(QTextCursor.Right,QTextCursor.MoveAnchor,len(u"애니메이션 "))
			tc.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor,len(u"애니메이션이름"))
			self.setTextCursor(tc)

	def wheelEvent(self,event):
		if event.modifiers() == Qt.ControlModifier:
			family = FontManager().FontName("NanumGothicCoding")

			if event.delta() < 0 :
				fnt = self.font()
				s = fnt.pointSize() - 1
				if s < 10 : 
					return 

				fnt.setPointSize(s)
				fnt.setFamily(family)
				self.setFont(fnt)	
				self.fontSizeAnim = 1000
			else:
				fnt = self.font()
				s = fnt.pointSize() + 1
				if s > 50 : 
					return 
					
				fnt.setPointSize(s)
				fnt.setFamily(family)
				self.setFont(fnt)
				self.fontSizeAnim = 1000
		else:
			super(ScriptEditor,self).wheelEvent(event)

	def copyOrCut(self,isCopy):
		tc = self.textCursor()
		if tc.anchor() == tc.position():
			# 블럭 없이 Ctrl+C, Ctrl+X 를 누를 경우, 줄 전체가 복사/잘라내기
			tc.movePosition(QTextCursor.StartOfLine)
			tc.movePosition(QTextCursor.EndOfLine,QTextCursor.KeepAnchor)

			textData = tc.selectedText() + "\n"
			cboard = qApp.clipboard()
			cboard.clear()
			mimeData = QMimeData()
			mimeData.setText(textData)
			data = QByteArray(1,chr(1))
			mimeData.setData("application/pini-mime;value=\"pini-text-extra\"",data)
			cboard.setMimeData(mimeData)

			if not isCopy:
				tc.removeSelectedText()

				if not tc.atEnd():
					tc.deleteChar()
			return True
		return False

	def copy(self):
		result = self.copyOrCut(True)

		if not result:
			super(ScriptEditor,self).copy()

	def cut(self):
		result = self.copyOrCut(False)

		if not result:
			super(ScriptEditor,self).cut()

	def paste(self):
		cboard = qApp.clipboard()

		if cboard != None:
			if cboard.mimeData().hasText():
				formats = cboard.mimeData().formats()

				datas = cboard.mimeData().data("application/pini-mime;value=\"pini-text-extra\"")

				if datas != None:
					if ord(datas[0]) == 1:
						# 블럭 없이 줄 복사 한 경우에 붙여넣기 시도시
						tc = self.textCursor()
						if tc.anchor() < tc.position():
							tc.setPosition(tc.anchor())
						tc.movePosition(QTextCursor.StartOfLine)
						tc.insertText(cboard.mimeData().text())
						return

		super(ScriptEditor,self).paste()

	def showReference(self):
		cmd,pos = self.currentCommand()
		url = ScriptCommand.GetReferenceUrl(cmd)

		if url != None:
			QDesktopServices.openUrl(QUrl(url))
		else:
			QDesktopServices.openUrl(QUrl("http://nooslab.com/piniengine/wiki"))

	def toggleSemicolon(self):
		self.toggleCharacter(";")

	def toggleComment(self):
		self.toggleCharacter("#")

	def toggleCharacter(self,char):
		tc = self.textCursor()
		pos = tc.position()
		anch = tc.anchor()

		startPos = 0
		endPos = 0

		if pos < anch:
			startPos = pos
			endPos = anch
		else :
			startPos = anch
			endPos = pos

		IsInsertFlag = False

		tc.clearSelection()
		tc.setPosition(startPos)
		tc.movePosition(QTextCursor.StartOfBlock)

		# 글자 없이 시작하는 문장이 있는지 확인합니다
		while 1:
			if tc.atEnd():
				break

			tc.movePosition(QTextCursor.StartOfBlock)
			curPos = tc.position()
			tc.movePosition(QTextCursor.EndOfLine)
			if curPos != tc.position():
				tc.movePosition(QTextCursor.StartOfBlock)
				tc.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor)

				while tc.selectedText == "\t":
					tc.clearSelection()
					tc.movePosition(QTextCursor.Right,QTextCursor,KeepAnchor)

				if tc.selectedText() != char:
					IsInsertFlag = True
					break

			tc.movePosition(QTextCursor.EndOfLine)
			if tc.atEnd():
				break
			tc.movePosition(QTextCursor.Right)

			if endPos < tc.position():
				break

		tc.clearSelection()
		tc.setPosition(startPos)
		tc.movePosition(QTextCursor.StartOfBlock)

		while 1:
			# 글자 추가 및 삭제때문에 끝나야 하는 위치가 바뀌므로, endPos 에 1을 더하거나 뺍니다
			if IsInsertFlag:
				pos = tc.position()
				tc.insertText(char)
				endPos += 1
			else:
				if tc.atEnd():
					break

				tc.movePosition(QTextCursor.StartOfBlock)
				curPos = tc.position()
				tc.movePosition(QTextCursor.EndOfLine)
				if curPos != tc.position():
					tc.movePosition(QTextCursor.StartOfBlock)
					tc.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor)

					if tc.selectedText() == char:
						tc.removeSelectedText()
						endPos -= 1

			tc.movePosition(QTextCursor.EndOfLine)
			if tc.atEnd():
				break
			tc.movePosition(QTextCursor.Right)

			if endPos < tc.position():
				break	

	def keyReleaseEvent(self,e):
		super(ScriptEditor,self).keyReleaseEvent(e)

	def isVirtualKey(self,key):
		# Key_Escape 는 가상 키코드의 시작값입니다.
		# 즉, Key_Escape 와 비교하면 가상키인지 확인이 가능합니다
		return key >= Qt.Key_Escape

	def inputMethodEvent(self,e):
		length = len(e.commitString())

		def inputMethodCallback():
			super(ScriptEditor,self).inputMethodEvent(e)

		if length==1:
			keyCode = ord(e.commitString()[0])
			result = self.keyInputProcess(keyCode,False,False,e,inputMethodCallback)
		else:
			inputMethodCallback()

	def keyPressEvent(self,e):
		def keyPressCallback():
			self.pressKey = e.key()
			super(ScriptEditor,self).keyPressEvent(e)
			self.pressKey = None

		self.keyInputProcess(e.key(),e.modifiers() == Qt.ControlModifier,e.modifiers() == Qt.ShiftModifier,e,keyPressCallback)

	def keyInputProcess(self,key,isCtrl,isShift,e,func):
		if self.mouseHoveringCloseDistance >= 0:
			# 설명창이 떠있던 상태에서 키보드 입력이 들어온다면, 끕니다.
			self.mouseHoveringCloseDistance = -1
			self.explainHoverWebView.resize(0,0)

		self.mouseHoveringCounter = -1 # 또한, 설명창이 뜨지 않게 합니다.

		if key == Qt.Key_Backspace:
			# 백스페이스키가 눌렸을 때의 행동입니다.
			tc = self.textCursor()

			if not (tc.atStart() or tc.atEnd()):
				tc.movePosition(QTextCursor.Left,QTextCursor.KeepAnchor)
				leftChar = tc.selectedText()
				tc.movePosition(QTextCursor.Right,QTextCursor.MoveAnchor)
				tc.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor)
				rightChar = tc.selectedText()

				isBrackets = leftChar == "[" and rightChar == "]"
				isParentheses = leftChar == "(" and rightChar == ")"
				isQuoting = leftChar == "\"" and rightChar == "\""
				isMarkup = leftChar == "<" and rightChar == ">"

				if isBrackets or isParentheses or isQuoting or isMarkup:
					tc.removeSelectedText()

		if isCtrl and (key == Qt.Key_Up or key == Qt.Key_Down):
			# Ctrl+↑, Ctrl+↓ 가 눌렸을 때의 행동입니다.
			movementValue = 1
			if key == Qt.Key_Up:
				movementValue = -1

			self.verticalScrollBar().setValue(self.verticalScrollBar().value() + movementValue)

			e.ignore()
			return

		if self.EnterIgnore : 
			if key in [Qt.Key_Enter,Qt.Key_Return] : 
				e.ignore()
				return

		if self.completer.popup().isVisible() :
			closeKeys = [Qt.Key_Left,Qt.Key_Right,Qt.Key_Escape]
			if key in closeKeys:
				e.ignore()
				self.completionClose()
				return 

			ignoreKeys=[Qt.Key_Tab,Qt.Key_Enter,Qt.Key_Return,Qt.Key_Backtab]
			if key in ignoreKeys: 
				e.ignore()
				return

		if key == Qt.Key_Tab or key == Qt.Key_Backtab :
			# 탭 또는 백탭이 눌렸을 때의 행동입니다.
			tc = self.textCursor()
			pos = tc.position()
			anch = tc.anchor()

			if pos != anch:
				# 블록 영역 선택 중일 때에만 작동합니다
				startPos = 0
				endPos = 0

				if pos < anch:
					startPos = pos
					endPos = anch
				else :
					startPos = anch
					endPos = pos

				tc.clearSelection()
				tc.setPosition(startPos)
				tc.movePosition(QTextCursor.StartOfLine)

				while 1:
					# 탭 추가 및 삭제때문에 끝나야 하는 위치가 바뀌므로, endPos 에 1을 더하거나 뺍니다
					if key == Qt.Key_Tab:
						tc.insertText("\t")
						endPos += 1
					else:
						if tc.atEnd():
							break

						curPos = tc.position()
						tc.movePosition(QTextCursor.EndOfLine)
						if curPos != tc.position():
							tc.movePosition(QTextCursor.StartOfLine)
							tc.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor)

							if tc.selectedText() == "\t":
								tc.removeSelectedText()
								endPos -= 1

					tc.movePosition(QTextCursor.EndOfLine)
					if tc.atEnd():
						break
					tc.movePosition(QTextCursor.Right)

					if endPos < tc.position():
						break

				return
			elif key == Qt.Key_Backtab:
				tc.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)

				sel = tc.selectedText()
				notTabFound = False

				for c in sel:
					if c != '\t':
						notTabFound = True
						break

				if not notTabFound:
					tc.clearSelection()
					tc.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)

					if tc.selectedText() == '\t':
						tc.removeSelectedText()

					return

		if key == Qt.Key_Ampersand or (key == Qt.Key_7 and isShift) :
			# & 이 눌렸을 때의 행동입니다.
			# 애니메이션 블록인지 체크해서, 아니라면 무시합니다.
			isAnimationBlock = False

			tc = self.textCursor()
			tc.movePosition(QTextCursor.StartOfBlock)
			while tc.blockNumber() > 0:
				if not tc.atBlockEnd():
					tc.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)

					if tc.selectedText() == "\t":
						tc.movePosition(QTextCursor.PreviousBlock)
						continue
					elif tc.selectedText() == "@":
						tc.movePosition(QTextCursor.EndOfWord, QTextCursor.KeepAnchor)

						if tc.selectedText() == u"@애니메이션":
							isAnimationBlock = True
							break
					else:
						break
				else:
					tc.movePosition(QTextCursor.PreviousBlock)

			if isAnimationBlock:
				self.insertText("&")

				import ATL
				animationTypes = ATL.line_Interval + ATL.line_Instant

				self.completionShow(QStringListModel(animationTypes),self.AnimationComplete)
				return

		if key == Qt.Key_BracketLeft :
			# '[' 키가 눌렸을 때의 행동입니다.
			if not isShift:
				self.insertText("[]")
				self.cursorMove(-1)
				
				commands = ScriptCommand.List()
				self.completionShow(QStringListModel(commands[0]),self.selectedCommand,commands[1])
				return

		if key == Qt.Key_BracketRight:
			# ']' 키가 눌렸을 때의 행동입니다.
			if not isShift:
				tc = self.textCursor()
				if not tc.atEnd():
					tc.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor)
					if tc.selectedText() == "]":
						self.cursorMove(1)
						return
					else:
						tc.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor)
						if tc.selectedText() == " ]":
							self.cursorMove(2)
							if self.completer.popup().isVisible() :
								self.completionClose()
							return

		if (key == Qt.Key_ParenLeft) or (key == Qt.Key_9 and isShift) :
			# '(' 키가 눌렸을 때의 행동입니다.
			tc = self.textCursor()

			pos = tc.position()
			anch = tc.anchor()

			if pos != anch:
				# 블록 영역 선택 중일 때에만 작동합니다
				startPos = 0
				endPos = 0

				if pos < anch:
					startPos = pos
					endPos = anch
				else :
					startPos = anch
					endPos = pos

				tc.clearSelection()
				tc.setPosition(startPos)
				tc.insertText("(")
				tc.setPosition(endPos)
				tc.movePosition(QTextCursor.Right)
				tc.insertText(")")
				tc.setPosition(startPos+1)
				tc.setPosition(endPos+1,QTextCursor.KeepAnchor)
				self.setTextCursor(tc)
				return

			else:
				self.insertText("()")
				self.cursorMove(-1)
				return

		if (key == Qt.Key_ParenRight) or (key == Qt.Key_0 and isShift) :
			# ')' 키가 눌렸을 때의 행동입니다.
			tc = self.textCursor()
			if not tc.atEnd():
				tc.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor)
				if tc.selectedText() == ")":
					self.cursorMove(1)
					return

		if (key == Qt.Key_QuoteDbl) or (key == Qt.Key_Apostrophe and isShift) :
			# '"' 키가 눌렸을 때의 행동입니다.
			tc = self.textCursor()

			pos = tc.position()
			anch = tc.anchor()

			if pos != anch:
				# 블록 영역 선택 중일 때에만 작동합니다
				startPos = 0
				endPos = 0

				if pos < anch:
					startPos = pos
					endPos = anch
				else :
					startPos = anch
					endPos = pos

				tc.clearSelection()
				tc.setPosition(startPos)
				tc.insertText("\"")
				tc.setPosition(endPos)
				tc.movePosition(QTextCursor.Right)
				tc.insertText("\"")
				tc.setPosition(startPos+1)
				tc.setPosition(endPos+1,QTextCursor.KeepAnchor)
				self.setTextCursor(tc)
				return

			elif not tc.atEnd():
				tc.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor)
				if tc.selectedText() == "\"":
					self.cursorMove(1)
					return
				else:
					self.insertText("\"\"")
					self.cursorMove(-1)
					return

		if key in [Qt.Key_Return,Qt.Key_Escape,Qt.Key_BracketRight,Qt.Key_Space] :
			self.completionClose()

		if key == Qt.Key_Escape:
			tc = self.textCursor()
			if tc.hasSelection():
				# 블럭 선택중 ESC 키가 눌릴 경우, 블럭 선택 해제하도록
				tc.clearSelection()
				self.setTextCursor(tc)

		if (key == 46 and isShift) or key == Qt.Key_Greater: # FOR WINDOW;; key , Qt.Key_Greater
			# '<' 키가 눌렸을 때의 행동입니다.
			text = self.textCursor().block().text()
			if len(text) == self.getIndent(text):
				self.insertText(">")
				self.completionShow(QStringListModel(self.bookmarkList()),self.BookmarkComplete)
				return 
			else:
				tc = self.textCursor()
				if not tc.atEnd():
					tc.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor)
					if tc.selectedText() == ">":
						self.cursorMove(1)
						return
					else:
						tc.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor)
						if tc.selectedText() == " >":
							self.cursorMove(2)
							if self.completer.popup().isVisible() :
								self.completionClose()
							return
					
		if (key == 44 and isShift) or key == Qt.Key_Less: # FOR WINDOW;; key , Qt.Key_Less
			# '>' 키가 눌렸을 때의 행동입니다.
			text = self.textCursor().block().text()
			if re.match(u"\t*[;,]",text):
				self.insertText("<>")
				self.cursorMove(-1)
				self.completionShow(self.markups,self.markupCompletion)
				return

		Enter_isSemicolonLine = False
		Enter_isColonLine = False
		Enter_countTabBlock = 0
		
		if key == Qt.Key_Return or key == Qt.Key_Enter:
			# 엔터키가 눌렸을 때의 행동입니다.
			c1 = self.findLine("]")
			c2 = self.findLine("[")
			if c1 and (c2 == None or c2.position() > c1.position()) :   
				if self.findLine("[",QTextDocument.FindBackward) : 
					cmd,pos = self.currentCommand()
					if isShift:
						self.prevArg(cmd,pos)
					else:	
						self.nextArg(cmd,pos)
					return
			else :
				tc = self.textCursor()
				tc.select(QTextCursor.LineUnderCursor)
				txt = tc.selectedText()
				if txt.startswith("\t") :
					ret = re.match("\t+",txt)
					if ret :
						ret = ret.group() 
						Enter_countTabBlock = ret.count("\t")

				txt = txt[Enter_countTabBlock:]
				if len(txt) > 1 and txt.startswith(";") :
					Enter_isSemicolonLine = True
				if len(txt) > 1 and txt.startswith(",") :
					Enter_isColonLine = True

				if not (Enter_isSemicolonLine or Enter_isColonLine):
					if txt[-1:] == ":" or txt[-2:] == ": ":
						Enter_countTabBlock = Enter_countTabBlock + 1

		if key == Qt.Key_Comma :
			# "," 가 눌렸을 때의 행동입니다.
			tc = self.textCursor()
			tc.select(QTextCursor.LineUnderCursor)
			txt = tc.selectedText()
			if re.match("\t*;$",txt):
				tc = self.textCursor()
				tc.movePosition(QTextCursor.EndOfBlock)
				tc.movePosition(QTextCursor.Left,QTextCursor.KeepAnchor)
				tc.removeSelectedText()

		if key == Qt.Key_Return or key == Qt.Key_Enter:
			if isShift:
				return 

		rs = False

		if not self.completer.popup().isVisible() :
			if not isCtrl :
				if not self.isVirtualKey(key) :
					tc = self.textCursor()
					tc.movePosition(QTextCursor.StartOfBlock)
					tc.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor)
					if tc.selectedText() == ">" :
						self.completionShow(QStringListModel(self.bookmarkList()),self.BookmarkComplete)
					else:
						try:
							rs = self.functionSuggestCompletionShow()
						except Exception, __:
							pass

		if (not rs) and (key == Qt.Key_Space) : 
			#if e.modifiers() == Qt.META or e.modifiers() == Qt.CTRL : 
			try:
				self.functionArguCompletionShow()
			except Exception, __:
				pass
				
		if (key == Qt.Key_2 and isShift) or key == Qt.Key_At :
			# @매크로 자동생성.

			tc = self.textCursor()
			blckNumber = tc.blockNumber()
			isEnable = True

			while True:
				b1 = tc.blockNumber() != blckNumber
				b2 = tc.atBlockStart()
				if b1 or b2:
					break

				tc.clearSelection()
				tc.movePosition(QTextCursor.Left,QTextCursor.KeepAnchor)
				sel = tc.selectedText()

				if sel == "\t":
					continue
				elif sel == "\n" or sel == "\r":
					break
				else:
					isEnable = False
					break

			if isEnable:
				# 줄의 처음에서만 자동완성이 뜹니다.
				self.completionShow( QStringListModel([u"@매크로",u"@조건",u"@애니메이션"]), self.BlockComplete )

		if isCtrl and key == Qt.Key_Slash:
			# Ctrl+/ 로 선택한 줄 전체 주석 처리 또는 주석 해제
			self.toggleComment()

			e.ignore()
			return

		if isCtrl and key == Qt.Key_V:
			self.paste()
			return

		if isCtrl and (key == Qt.Key_C or key == Qt.Key_X):
			if key == Qt.Key_X:
				self.cut()
			else:
				self.copy()
			return

		func()

		if (key == Qt.Key_Return or key == Qt.Key_Enter) and Enter_countTabBlock > 0 : 
			self.insertText('\t'*Enter_countTabBlock)

		if (key == Qt.Key_Return or key == Qt.Key_Enter) and Enter_isSemicolonLine:
			self.insertText(";")

		if (key == Qt.Key_Return or key == Qt.Key_Enter) and Enter_isColonLine:
			self.insertText(",")

		if key in [Qt.Key_Left,Qt.Key_Up,Qt.Key_Right,Qt.Key_Down,Qt.Key_PageUp,Qt.Key_PageDown] :
			self.updateLine()

	def lineNumberAreaPaintEvent(self,event):
		painter = QPainter(self.lineNumber)
		painter.fillRect(event.rect(), QColor(80,80,80, 255))

		block = self.firstVisibleBlock()
		blockNumber = block.blockNumber()
		top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
		bottom = top + int(self.blockBoundingRect(block).height())

		currentBlockNumber = self.textCursor().block().blockNumber()

		painter.setFont(self.font())
		while block.isValid() and top <= event.rect().bottom() :
			if block.isVisible() and bottom >= event.rect().top() :
				number = str(blockNumber + 1)
				if currentBlockNumber == blockNumber : 
					painter.setPen(QColor(255,255,255));
				else:
					painter.setPen(QColor(143,144,138));
				painter.drawText(0, top, self.lineNumber.width()-1, self.fontMetrics().height(), Qt.AlignRight | Qt.AlignVCenter, number);

			block = block.next()
			top = bottom
			bottom = top+int(self.blockBoundingRect(block).height())
			blockNumber += 1

	def lineNumberAreaWidth(self):
		digits = 1
		_max = max(1, self.blockCount())
		while _max >= 10:
			_max /= 10
			digits += 1
		return 8 + self.fontMetrics().width(self.trUtf8('9')) * digits

	def resizeEvent(self,e):
		super(ScriptEditor,self).resizeEvent(e)
		r = self.contentsRect();
		self.lineNumber.setGeometry(QRect(r.left(), r.top(), self.lineNumberAreaWidth(), r.height()))

	def tempSaveFinish(self):
		self.tempSaveFin = 0
		self._tempSaveThread = None

	def getTempFileName(self):
		targetPath = self.sceneCtrl.path
		targetPath = targetPath.replace("\\","/")
		targetPath = targetPath.replace(ProjectController()._path.replace("\\","/")+"/scene/","")
		targetPath = targetPath.replace(".lnx",".tmp")
		targetPath = targetPath.replace("/","__!_")	
		return targetPath

	def tempSave(self):
		self.tempSaveTimer.stop()
		if self.tempSaveFin == 0 : 
			targetPath = self.getTempFileName()
			self._tempSaveThread = TempSaveThread(targetPath, self.toPlainText())
			self._tempSaveThread.finished.connect(self.tempSaveFinish)
			self._tempSaveThread.start()
		self.tempSaveFin = 1

	def scriptChanged(self,froms,removes,adds):
		if self.sceneCtrl:
			self.sceneCtrl.needSave = True
			self.sceneScriptWindow.setNeedSaveStatus(True)
			self.tempSaveTimer.stop()
			self.tempSaveTimer.start(1000)

		if self.completer.popup().isVisible() and self.EnterIgnore == False :
			idx=0
			underText = self.textUnderCursor()
			underText = underText.replace("\"","").replace("]","").replace(">","")
			if len(underText) > 0 :
				for v in self.completer.model().stringList() : 
					if v.startswith(underText) : 
						self.completer.popup().setCurrentIndex(self.completer.completionModel().index(idx,0))
						break
					idx += 1

	def updateLineNumberAreaWidth(self,blocks):
		if blocks > 0 :
			if self.prevBlockCount > blocks :
				offset = self.prevBlockCount-blocks
				start = self.textCursor().blockNumber()

				self.commandRemove(start,offset);

			elif self.prevBlockCount < blocks:
				if self.noCommmandAdd == None:
					offset = blocks-self.prevBlockCount
					start = self.textCursor().blockNumber()-offset+1
					self.commandAdd(start,offset);

			self.prevBlockCount = blocks
			self.commandUpdate(self.textCursor().blockNumber()-1)
			self.commandUpdate(self.textCursor().blockNumber())

		self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0);

	def updateLineNumberArea(self,rect,dy):
		if dy:
			self.lineNumber.scroll(0, dy)
		else:
			self.lineNumber.update(0, rect.y(), self.lineNumber.width(), rect.height())

		if rect.contains(self.viewport().rect()) :
			self.updateLineNumberAreaWidth(0)

	def cursorMove(self,offset=1):
		cur = self.textCursor()
		if offset > 0:
			for i in range(0,offset):
				cur.movePosition(QTextCursor.Right)
		elif offset < 0:
			for i in range(0,-offset):
				cur.movePosition(QTextCursor.Left)
		self.setTextCursor(cur)

	def cursorMoveLine(self,offset=1):
		cur = self.textCursor()
		cur.movePosition(QTextCursor.NextRow)
		self.setTextCursor(cur)

	def currentArgument(self,targetCursor=None):
		if targetCursor == None:
			targetCursor = self.textCursor()

		tc = QTextCursor(targetCursor)
		blckNumber = tc.blockNumber()
		intentCount = 0
		isQuoting = False

		while 1:
			# 먼저 쌍따옴표 안인지 밖인지 판단합니다
			b1 = tc.blockNumber() != blckNumber
			b2 = tc.blockNumber() == 0 and tc.position() == 0
			if b1 or b2 :
				break

			tc.movePosition(QTextCursor.Left,QTextCursor.KeepAnchor)
			sel = tc.selectedText()

			if sel == "\"":
				isQuoting = not isQuoting

			tc.clearSelection()

		if not isQuoting:
			return ("",0)

		tc = QTextCursor(targetCursor)

		while 1:
			b1 = tc.blockNumber() != blckNumber
			b2 = tc.blockNumber() == 0 and tc.position() == 0
			if b1 or b2 :
				break

			tc.movePosition(QTextCursor.Left,QTextCursor.KeepAnchor)
			sel = tc.selectedText()

			if isQuoting:
				if sel == "\"":
					isQuoting = not isQuoting
			else:		
				if sel == "\"":
					isQuoting = not isQuoting
				elif sel == " ":
					break
				elif sel == "=":
					tc.movePosition(QTextCursor.Left)
					tc.select(QTextCursor.WordUnderCursor)
					return (tc.selectedText(),tc.position())
				elif sel == "[":
					if intentCount == 0 :
						break
					intentCount -= 1
				elif sel == "]":
					intentCount += 1

			tc.clearSelection()
		return ("",0)

	def currentCommand(self,targetCursor=None):
		if targetCursor == None:
			targetCursor = self.textCursor()

		tc = QTextCursor(targetCursor)
		blckNumber = tc.blockNumber()
		intentCount = 0
		isQuoting = False

		while 1:
			# 먼저 쌍따옴표 안인지 밖인지 판단합니다
			b1 = tc.blockNumber() != blckNumber
			b2 = tc.blockNumber() == 0 and tc.position() == 0
			if b1 or b2 :
				break

			tc.movePosition(QTextCursor.Left,QTextCursor.KeepAnchor)
			sel = tc.selectedText()

			if sel == "\"":
				isQuoting = not isQuoting

			tc.clearSelection()

		tc = QTextCursor(targetCursor)

		while 1:
			b1 = tc.blockNumber() != blckNumber
			b2 = tc.blockNumber() == 0 and tc.position() == 0
			if b1 or b2 :
				break

			tc.movePosition(QTextCursor.Left,QTextCursor.KeepAnchor)
			sel = tc.selectedText()

			if isQuoting:
				if sel == "\"":
					isQuoting = not isQuoting
			else:
				if sel == "\"":
					isQuoting = not isQuoting
				elif sel == "[":
					if intentCount == 0 :
						tc.movePosition(QTextCursor.Right)
						tc.select(QTextCursor.WordUnderCursor)
						return (tc.selectedText(),tc.position())
					intentCount -= 1
				elif sel == "]":
					intentCount += 1

			tc.clearSelection()
		return ("",0)

	def currentMarkup(self):
		tc = self.textCursor()
		blckNumber = tc.blockNumber()
		isQuoting = False
		while 1:
			b1 = tc.blockNumber() != blckNumber
			b2 = tc.blockNumber() == 0 and tc.position() == 0
			if b1 or b2 :
				break

			tc.movePosition(QTextCursor.Left,QTextCursor.KeepAnchor)
			sel = tc.selectedText()
			if sel == "<":
				if isQuoting :
					tc.movePosition(QTextCursor.Right)
					tc.select(QTextCursor.WordUnderCursor)
					return (tc.selectedText(),tc.position())
			elif sel == "\"":
				isQuoting = not isQuoting

			tc.clearSelection()
		return ("",0)

	def currentArgIdx(self):
		pass

	def findLine(self,s,opt=None,cursor=None):
		if cursor == None : 
			cursor = self.textCursor()
		curLine = cursor.blockNumber()
		if opt:
			cursor = self.document().find(s,cursor,opt)
		else:
			cursor = self.document().find(s,cursor)
		if cursor.position() is -1 or cursor.blockNumber() != curLine :
			return None
		return cursor

	def findAssignInLine(self,opt=None):
		cursor1 = self.findLine("=",opt)
		return cursor1
		'''
		cursor2 = None
		cursor = self.textCursor()
		while True:
			cursor2 = self.findLine(QRegExp(r'\".*=.*\"'),opt,cursor)
			print "find expr",cursor2
			if cursor2 == None : 
				break
			print "comp",cursor2.position(),len(cursor2.selectedText()) , self.textCursor().position()
			if cursor2.position() < self.textCursor().position() : 
				break
			cursor.movePosition(QTextCursor.Left,QTextCursor.MoveAnchor,1)
			print "move left!"

		print cursor2,cursor1
		if cursor2 and cursor1 : 
			p1 = cursor1.position()
			p2 = cursor2.position()
			p3 = len(cursor2.selectedText())
			print "yo,check!",p1,p2,p3
			if p2 < p1 and p2+p3 > p1 :
				return None
		if cursor1 : 
			return cursor1
		return None
		'''

	def checkArg(self,cursor,cmd,pos,doStep=True):
		self.setTextCursor(cursor)
		cur = self.findLine("\"")
		if cur : 
			self.cursorMove(cur.position() - self.textCursor().position())
			cur = self.findLine("\"")
			if cur : 
				offset = cur.position() - self.textCursor().position()-1
				if offset > 0 :
					cursor = self.textCursor()
					cursor.movePosition(QTextCursor.Right,QTextCursor.MoveAnchor,offset)
					cursor.movePosition(QTextCursor.Left,QTextCursor.KeepAnchor,offset)
					self.setTextCursor(cursor)
		else:
			cursor.select(QTextCursor.WordUnderCursor)
			count = len(cursor.selectedText())
			
			cursor.clearSelection()
			cursor.movePosition(QTextCursor.Left,QTextCursor.KeepAnchor,count)
			self.setTextCursor(cursor)

		_tc = self.textCursor()
		_tc.movePosition(QTextCursor.Left,QTextCursor.MoveAnchor,4)
		_tc.select(QTextCursor.WordUnderCursor)

		argName = _tc.selectedText()

		if doStep:
			ScriptCommand.Step(self,cmd,argName)
		return True

	def currentArg(self,cmd,pos):
		cursor = self.findAssignInLine(QTextDocument.FindBackward)
		if cursor is None :
			cursor = self.findLine("[",QTextDocument.FindBackward)
			if cursor : 
				cursor.clearSelection()
				self.setTextCursor(cursor)
			return False
		
		self.setTextCursor(cursor)
		return self.checkArg(cursor,cmd,pos,False)

	def prevArg(self,cmd,pos):
		for v in range(0,2):
			cursor = self.findAssignInLine(QTextDocument.FindBackward)
			if cursor is None :
				cursor = self.findLine("[",QTextDocument.FindBackward)
				if cursor : 
					cursor.clearSelection()
					self.setTextCursor(cursor)
				return False
			
			if cursor.position() - self.textCursor().position() < -1 :
				break 
			self.cursorMove(-2)

		self.setTextCursor(cursor)
		return self.checkArg(cursor,cmd,pos)

	def nextArg(self,cmd,pos):
		cursor = self.findAssignInLine()
		if cursor is None :
			cursor = self.findLine("]")
			if cursor is None:
				return False
			cursor.clearSelection()

			tc = self.findLine("[",QTextDocument.FindBackward)

			while tc.selectedText()[-1] != "]":
				tc.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor)

			obj = ScriptCommand.GenObjLine(tc.selectedText())

			if obj:
				rebuildMacro = "["
				rebuildMacro += obj[0]["name"]
				if obj[0]["args"] != None:
					for v in obj[0]["args"]:
						rebuildMacro += " "
						rebuildMacro += v["l"]["v"]
						rebuildMacro += "="
						rebuildMacro += self.CALCULATE_PART(v["r"])
				rebuildMacro += "]"

				tc.insertText(rebuildMacro)

			indent = self.getIndent(self.textCursor().block().text())
			cursor.insertText("\n")
			cursor.insertText("\t"*indent)

			if cmd == u"독백" or cmd == u"대화":
				cursor.insertText(";")

			self.setTextCursor(cursor)
			return False

		return self.checkArg(cursor,cmd,pos)

	def updateErrorLine(self):
		extraSelections = []
		block = self.firstVisibleBlock().previous()
		if block.blockNumber() == -1:
			block = self.document().firstBlock()

		errorColor = QColor(Qt.red).lighter(40)
		warningColor = QColor(Qt.yellow).lighter(30)
		bookmarkColor = QColor(100,100,100)
		
		def makeSec(block,color):
			selection = QTextEdit.ExtraSelection()

			selection.format.setBackground(color)
			selection.format.setProperty(QTextFormat.FullWidthSelection, True)
			selection.cursor = QTextCursor(block)
			selection.cursor.clearSelection()

			return selection

		lineCount = (int(self.contentsRect().height()) / int(self.blockBoundingRect(block).height())) + 2
		i = 0

		while block :
			if block.isVisible() == False : 
				break
			if i > lineCount:
				break

			bn = block.blockNumber()
			if bn < 0 or len(self.compiledCommand) <= bn : 
				break 

			cc = self.compiledCommand[bn]
			if cc : 
				c  = cc["compiled"]
				if c == False : 
					#print "retry",bn

					extraSelections.append(makeSec(block,errorColor))
					self.compilingThread.enqueueCompile(True,None,bn)
					# 재시도는 다음 타이머 작동시에 처리합니다.

				elif c and c[1][0]["t"] == LNXOptimizer.cmd("bookmark"):
					extraSelections.append(makeSec(block,bookmarkColor))
				elif cc["warning"] : 
					#print "warning retry",bn

					extraSelections.append(makeSec(block,warningColor))
					self.compilingThread.enqueueCompile(True,None,bn)
					# 재시도는 다음 타이머 작동시에 처리합니다.

			block = block.next()
			i = i + 1
		self.setExtraSelections(extraSelections)

	def insertText(self,text):
		cur = self.textCursor()
		cur.insertText(text)

	def removeSelectedText(self):
		cur = self.textCursor()
		cur.removeSelectedText()

	def OnCompilingThreadBeginBusy(self,isBusy):
		#print "BeginBusy: ",isBusy
		pass

	def OnCompilingThreadCallback(self,callback):
		callback[0]()

	def compiledText(self,text,isInBlock=False,blockIdx=False):
		self.bookmarks = []
		c=False

		try:
			c = ScriptCommand.CompileLine(text)
		except Exception, e:
			pass
		bookmark = None
		goto = None
		warning = False
		try:
			if c :
				v = c[1][len(c[1])-1]
				if v["t"] == LNXOptimizer.cmd("bookmark"):
					bookmark = v["name"]
				elif v["t"] == LNXOptimizer.cmd("goto") or v["t"] == LNXOptimizer.cmd("hypergoto"): 
					goto = v["goto"]["v"]
				elif v["t"] == LNXOptimizer.cmd("call"):

					if v["name"] == u"이미지" or v["name"] == u"터치영역":
						for argu in v["args"]:
							if argu["l"]["v"] == u"북마크이동":
								goto = argu["r"]["v"]
				else:
					#대사줄 중에 <연결> 마크업을 찾습니다

					loopBreak = False
					for statement in reversed(c[1]):
						if statement["t"] == LNXOptimizer.cmd("markup"):
							if statement["name"] == u"연결":
								goto = statement["args"][0]
								break

						if statement["t"] == LNXOptimizer.cmd("word"):
							for ch in statement["strs"]:
								if ch == "\\n":
									loopBreak = True
									break
							if loopBreak:
								break
		except Exception, e:
			traceback.print_exc(file=sys.stdout)

		return {"text":text,
				"compiled":c,
				"goto":goto,
				"bookmark":bookmark,
				"blockIdx":blockIdx,
				"isInBlock":isInBlock,
				"warning":warning}

	def compileAll(self):
		self.compilingThread.enqueueCompile(False)

	def getIndent(self,text):
		ret = re.match("\t*",text)
		if ret.start() == 0 : 
			return len(ret.group())
		return 0

	def compileBlockNumber(self,line,update):
		cpc = self.compiledCommand
		i = line
		block = self.document().findBlockByLineNumber(line);

		isInBlock = False
		blockIdx = False

		text = block.text()
		blockFind = re.match('\t+',text)

		def findUpCompile(i,text) : 
			while True:
				i -= 1 
				if i < 0 :
					break
				btext = self.document().findBlockByLineNumber(i).text()
				if re.match(text,btext) :
					self.compileBlockNumber(i,True)
					return i
			return -1

		if re.match(u"\t*@조건",text) : 
			curIndent = self.getIndent(text)
			while True :
				i = i + 1
				if i > self.blockCount():
					break

				btext = self.document().findBlockByLineNumber(i).text()
				indent = self.getIndent(btext)
				_text = btext[indent:]

				if indent > curIndent : 
					if _text.startswith(u"@다른조건") or \
					   _text.startswith(u"@그외"): 
						text = text + "\n" + btext + "\n" + ("\t"*(indent+1))+"pass"
					else:
						text = text + "\n" + btext
				else : 
					if indent != len(btext):
						break
			
			blockIdx = self.blockIdx
			self.blockIdx += 1

		elif re.match(u"\t*@매크로|\t*@애니메이션",text) : 
			curIndent = self.getIndent(text)
			while True :
				i = i + 1
				if i > self.blockCount():
					break
				
				btext = self.document().findBlockByLineNumber(i).text()
				indent = self.getIndent(btext)
				_text = btext[indent:]
				if indent > curIndent : 
					_text = btext[curIndent:]
					text = text + "\n" + _text
				else : 
					if indent != len(btext):
						break;

			blockIdx = self.blockIdx
			self.blockIdx += 1

		elif re.match(u"\t*@다른조건|\t*@그외",text): 
			curIndent = self.getIndent(text)
			text += "\n"+("\t"*(curIndent+1))+"pass"
			while True :
				i -= 1 
				if i < 0 :
					break
				btext  = self.document().findBlockByLineNumber(i).text()
				indent = self.getIndent(btext)
				_text  = btext[indent:]
				if _text : 
					if _text.startswith(u"@다른조건") :
						text = btext + "\n"+("\t"*(indent+1))+"pass\n" + text
					else:
						text = btext+"\n"+text
					if curIndent == indent : 
						if _text.startswith(u"@조건") : 
							if indent != len(btext):
								break;

			blockIdx = self.blockIdx
			self.blockIdx += 1

		elif re.match(u"\t*@노드|\t*@프레임",text) : 
			text = ""
			findUpCompile(i,u"\t*@애니메이션")

		elif re.match(u"\t+&",text):
			curIndent = self.getIndent(text)
			text = text[0:curIndent]

			findUpCompile(i,u"\t*@애니메이션")
			
		elif blockFind and blockFind.start() == 0 :
			## 현재 라인이 들여쓰기 중인 경우, 블럭넘버를 알맞게 매긴다
			isInBlock = True
			currentIndent = len(blockFind.group())

			while 1:
				if i < 0:
					break

				indenterLine = findUpCompile(i,u"\t*@매크로|\t*@조건|\t*@다른조건|\t*@그외")
				if currentIndent == len(text) : 
					text=""
					i -= 1
					continue

				nextIndent = self.getIndent(self.document().findBlockByLineNumber(indenterLine).text())
				if (currentIndent > nextIndent):
					break
				i -= 1

			if indenterLine != -1:
				blockIdx = cpc[indenterLine]["blockIdx"]
		else : 
			pass#re.match('\"\"',text)

		indent = re.match('\t+',text)
		if indent and indent.start() == 0:
			indent = indent.group().count("\t")
			text = ("\n"+text).replace("\n"+'\t'*indent,"\n")

		## 이전 텍스트랑 다르면 컴파일을 진행한다!
		_compile = None
		if update and len(cpc) > line:
			if cpc[line]["text"] != text or cpc[line]["warning"] :
				_compile = self.compiledText(text,isInBlock,blockIdx)
				cpc[line] = _compile
			else:
				_compile = cpc[line]
		else:	
			_compile = self.compiledText(text,isInBlock,blockIdx)
			cpc.insert(line,_compile)

	def commandUpdate(self,line):
		cpc = self.compiledCommand
		if line < 0 or line >= len(cpc) or self.prevBlockCount != self.blockCount():
			return

		def compileCallback():
			## 프리뷰를 갱신한다.
			self.commitGraphics()

		self.compilingThread.enqueueCompile(True,compileCallback,line)

	def commandAdd(self,start,offset):
		self.bookmarks = []

		def compileCallback():
			self.commitGraphics()

		self.compilingThread.enqueueCompile(False,compileCallback,start,offset)
		
	def commandRemove(self,start,offset):
		self.bookmarks = []
		cpc = self.compiledCommand
		for i in range(0,offset):
			del self.compiledCommand[start+1]
		self.commitGraphics()

	def buildFinished(self):
		self.previewUpdate = False
		self.buildThread = None
	
		projCtrl = ProjectController()

		self.sceneCtrl.view.scene.clear()
		self.sceneCtrl.view.scene.setScreenSize(projCtrl.screenWidth,projCtrl.screenHeight)
		
		protocol = ScriptGraphicsProtocol()
		for v in protocol.attachNode : 
			self.sceneCtrl.view.scene.addItem(v)
		for v in protocol.errorLog : 
			OutputWindow().notice(u"이미지 불러오기 실패 : "+v)
		try:
			for k,v in protocol.Logs.items() :
				OutputWindow().notice(v)
		except Exception, e:
			pass
		
		VariableViewWindow().previewInfoUpdate(protocol.lua)

		self.sceneCtrl.view.update()
		self.sceneCtrl.view.fitInView()

	def commitGraphics(self):
		if self.sceneCtrl and self.previewUpdate == False :
			self.previewUpdate = True
			def ___():
				pn = self.textCursor().blockNumber()
				cm = self.compiledCommand
				scene = self.sceneCtrl

				protocol = ScriptGraphicsProtocol()
				protocol.clear()

				self.buildThread = ComplieThread(scene,pn,cm)
				self.buildThread.finished.connect(self.buildFinished)
				self.buildThread.start()

			QTimer.singleShot(50, ___)
