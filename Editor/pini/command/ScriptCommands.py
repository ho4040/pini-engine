# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from PySide.QtGui import *
from PySide.QtCore import *
from command.FontManager import FontManager
import re
import os

from controller.ProjectController import ProjectController
from compiler import *
from lupa import LuaRuntime

from config import *
from Noriter.views.NoriterMainWindow import *

import time
import traceback
import os_encoding
import string

import ATL

import types

class GraphicsProtocolObject(object):
	_instance = None
	_isInit   = False
	def __new__(cls, *args, **kwargs):
		if not GraphicsProtocolObject._instance:
			GraphicsProtocolObject._instance = super(GraphicsProtocolObject,cls).__new__(cls,*args,**kwargs)

		return GraphicsProtocolObject._instance

	def __init__(self):
		if GraphicsProtocolObject._isInit:
			return
		GraphicsProtocolObject._isInit = True

		self.loaded = {}
	
	def LoadImg(self,src):
		if src in self.loaded : 
			return self.loaded[src]
				
		img  = QImage(src)
		size = img.size()
		if img.size().width() > 900 or img.size().height() > 900 : 
			img=img.scaled(900,900,Qt.KeepAspectRatio)
		
		self.loaded[src] = (img,size)
		return self.loaded[src]

	def ImgClear(self):
		self.loaded = {}

	class Slider(QGraphicsItem):
		def __init__(self,data):
			super(GraphicsProtocolObject.Slider,self).__init__()

			self.img1 = os.path.join(ProjectController().path,"image",data.img1)
			#self.img2 = os.path.join(ProjectController().path,"image",data.img2)
			self.img3 = os.path.join(ProjectController().path,"image",data.img3)

			self.origin1,size1 = GraphicsProtocolObject().LoadImg(self.img1)
			#self.origin2,size2 = GraphicsProtocolObject().LoadImg(self.img2)
			self.origin3,size3 = GraphicsProtocolObject().LoadImg(self.img3)

			loaded = self.origin1.rect()
			self.optimizScaleX = float(size1.width())/float(loaded.width())
			self.optimizScaleY = float(size1.height())/float(loaded.height())

			self.size1 = size1
			self.size3 = size3

			self.anchorX = 0.5
			self.anchorY = 0.5

			self.setPos(float(data.x),float(data.y))

		def boundingRect(self):
			w = self.size1.width()  * self.optimizScaleX
			h = self.size1.height() * self.optimizScaleY
			return QRect(-w * self.anchorX,-h * (1-self.anchorY),w,h) if self.origin1 else QRect(0,0,0,0)

		def paint(self, painter, option, widget):
			if self.origin1:
				thumbPos = QPoint( -self.size1.width()/2 - self.size3.width()/4 , -self.size1.height()/2  - self.size3.height()/4 )

				painter.setRenderHint( QPainter.HighQualityAntialiasing )
				painter.drawImage(self.boundingRect(),self.origin1,self.origin1.rect())
				painter.drawImage(QRect(thumbPos,self.size3),self.origin3,self.origin3.rect())
			return True

	class Node(QGraphicsItem):
		def __init__(self,v):
			super(GraphicsProtocolObject.Node,self).__init__()
			self.setPos(float(v.x),float(v.y))
			self.scale(float(v.scaleX),float(v.scaleY))
			self.setRotation(v.rotate)

			self.anchorX = v.anchorX
			self.anchorY = v.anchorY

		def boundingRect(self):
			return QRect(0,0,0,0)

		def paint(self, painter, option, widget):
			return True

	class Image(QGraphicsItem):
		def __init__(self,data):
			super(GraphicsProtocolObject.Image,self).__init__()
			self.r = 255
			self.g = 255
			self.b = 255
			self.a = 255
			self.origin = None
			self.size = None
			self.opacity = 1
			
			src = os.path.join(ProjectController().path,"image",data.path)
			if QFile(src).exists() :
				self.origin,size = GraphicsProtocolObject().LoadImg(src)
				self.generateColorImage()

				loaded = self.origin.rect()

				self.optimizScaleX = float(size.width())/float(loaded.width())
				self.optimizScaleY = float(size.height())/float(loaded.height())

				self.size = loaded
			else:
				self.origin = None
				self.size = QSize(0,0);

				self.optimizScaleX = 0
				self.optimizScaleY = 0
			
			self.setRotation(data.rotate)
			self.setOpacity(float(data.opacity)/255.0)
			self.setColor(float(data.color[1]),float(data.color[2]),float(data.color[3]))
			self.scale(float(data.scaleX),float(data.scaleY))
			self.setPos(float(data.x),float(data.y))

			self.anchorX = data.anchorX
			self.anchorY = data.anchorY

		def generateColorImage(self):
			if self.origin == None : return 

			c = QImage(self.origin.rect().width(),self.origin.rect().height(),QImage.Format_ARGB32_Premultiplied)
			self.color = QImage(self.origin.rect().width(),self.origin.rect().height(),QImage.Format_ARGB32_Premultiplied)
			
			c.fill(QColor(self.r,self.g,self.b));
			painter = QPainter(self.color);

			painter.fillRect(self.origin.rect(),Qt.transparent);
			painter.drawImage(0, 0, c);

			painter.setCompositionMode(QPainter.CompositionMode_Multiply);
			painter.drawImage(0, 0, self.origin);

			painter.setCompositionMode(QPainter.CompositionMode_DestinationOver);
			painter.end();

			self.color.setAlphaChannel(self.origin.alphaChannel());

		def setColor(self,r,g,b):
			if self.r != r or self.g != g or self.b != b : 
				self.r = r
				self.g = g
				self.b = b
				self.generateColorImage()
		
		def setOpacity(self,a):
			self.opacity = a

		def boundingRect(self):
			w = self.size.width()  * self.optimizScaleX
			h = self.size.height() * self.optimizScaleY
			return QRect(-w * self.anchorX,-h * (1-self.anchorY),w,h) if self.origin else QRect(0,0,0,0)

		def paint(self, painter, option, widget):
			if self.origin:
				painter.setOpacity(self.opacity)
				painter.setRenderHint( QPainter.HighQualityAntialiasing )
				painter.drawImage(self.boundingRect(),self.color,self.origin.rect())
			return True

		def setSize(self,x,y):
			if self.origin:
				self.size = QRect(0,0,x,y)

	class Label(QGraphicsItem):
		def __init__(self,v):
			super(GraphicsProtocolObject.Label,self).__init__()
			font = FontManager().FontName(v.font)
			self.font = QFont(font,float(v.size))
			self.font.setPixelSize(float(v.size))

			self.text = v.text
			self.fontMetrics = QFontMetrics(self.font)
			b = self.fontMetrics.boundingRect(self.text)
			self.rect = QRect(-b.width()*v.anchorX,-float(v.size)*v.anchorY,b.width(),float(v.size))

			self.color = QColor(float(v.color[1]),float(v.color[2]),float(v.color[3]))
			self.opacity = float(v.opacity)
			self.setRotation(v.rotate)
			self.scale(float(v.scaleX),float(v.scaleY))
			self.setPos(float(v.x),float(v.y))

			self.anchorX = v.anchorX
			self.anchorY = v.anchorY

		def boundingRect(self):
			return self.rect

		def outlineRect(self,s):
			return QRect(self.rect.x()-s/2,self.rect.y()-s/2,self.rect.width()+s/2,self.rect.height()+s/2)

		def paint(self, painter, option, widget):
			painter.setOpacity(self.opacity)
			painter.setPen(QPen(self.color))
			painter.setFont(self.font)
			painter.setRenderHint( QPainter.HighQualityAntialiasing )

			painter.drawText(self.boundingRect(),Qt.AlignCenter,self.text)
			return True

	class ColorLayer(QGraphicsItem):
		def __init__(self,v):
			super(GraphicsProtocolObject.ColorLayer,self).__init__()
			self.color = QColor(float(v.color[1]),float(v.color[2]),float(v.color[3]),float(v.opacity))
			self.width = float(v.width)
			self.height = float(v.height)
			self.setPos(float(v.x),float(v.y)-self.height)
			self.scale(float(v.scaleX),float(v.scaleY))
			self.setRotation(v.rotate)

			self.anchorX = v.anchorX
			self.anchorY = v.anchorY

		def boundingRect(self):
			return QRect(-self.width*self.anchorX,-self.height*(1-self.anchorY),self.width,self.height)

		def paint(self, painter, option, widget):
			painter.setPen(QPen(QColor(0,0,0,0)))
			painter.setBrush(QBrush(self.color))
			painter.drawRect(self.boundingRect())
			return True

	class LuaHelper(object):
		def __init__(self):
			self.textSize = {}

		def imageSize(self,path):
			src = ProjectController().path+QDir.separator()+"image"+QDir.separator()+path
			img,size = GraphicsProtocolObject().LoadImg(src);
			return [size.width(),size.height()]

		def fontSize(self,text,size,font):
			font = os.path.splitext(font)[0]
			font = FontManager().FontName(font)

			strSize = str(size)
			if text in self.textSize : 
				if strSize in self.textSize[text] : 
					if font in self.textSize[text][strSize]:
						return self.textSize[text][strSize][font]

			f = QFont(font,size)
			f.setPixelSize(size+1)
			b = QFontMetrics(f).boundingRect(text)
			w,h = b.width(),b.height()
			
			if w == 1 : 
				f = size/10
				if f == 0 : 
					f = 1
				w = (f*2)-1

			if not text in self.textSize :
				self.textSize[text] = {}
			if not strSize in self.textSize[text] :
				self.textSize[text][strSize] = {}
			if not font in self.textSize[text][strSize] :
				self.textSize[text][strSize][font] = None

			self.textSize[text][strSize][font] = [w,h]
			return self.textSize[text][strSize][font]

		def projPath(self):
			return ProjectController().path.encode(os_encoding.cp())

		def buildPath(self):
			return (ProjectController().path+"/build/").encode(os_encoding.cp())

class ScriptGraphicsProtocol(object):
	_instance = None
	_isInit   = False
	def __new__(cls, *args, **kwargs):
		if not ScriptGraphicsProtocol._instance:
			ScriptGraphicsProtocol._instance = super(ScriptGraphicsProtocol,cls).__new__(cls,*args,**kwargs)

		return ScriptGraphicsProtocol._instance

	def __init__(self):
		if ScriptGraphicsProtocol._isInit:
			return

		ScriptGraphicsProtocol._isInit = True
		self.sceneCtrl = None
		self.funcsInfo = None
		self.attachNode = []
		self.errorLog = []
		self.luaInit()

	def luaInit(self):
		self.lua = LuaRuntime()
		############ FOR TEST ############
		PROJPATH = ProjectController().path.replace(QDir.separator(),"/")
		BUILDPATH = PROJPATH + u"/build/?.lua;"
		BUILDPATH1 = PROJPATH + u"/build/scene/?.lua;"
		BUILDPATH2 = PROJPATH + u"/build/module/?.lua;"

		BUILDPATH = BUILDPATH.encode(os_encoding.cp())
		BUILDPATH1 = BUILDPATH1.encode(os_encoding.cp())
		BUILDPATH2 = BUILDPATH2.encode(os_encoding.cp())
		
		self.lua.execute("package.path = \"\"")
		self.lua.execute("function packagePath(path) package.path = package.path .. ';'..path end")		
		self.lua.globals().packagePath(BUILDPATH)
		self.lua.globals().packagePath(BUILDPATH1)
		self.lua.globals().packagePath(BUILDPATH2)
		
		self.XVM = None

		if config.__RELEASE__ == False :
			self.lua.execute("package.path = package.path .. ';../../novel/VisNovel/src/?.lua;'")
		else:
			self.lua.execute("package.path = package.path .. ';./lua/src/?.lua;'")
			self.lua.execute("package.path = package.path .. ';./lua/?.lua;'")
		##################################
		try:
			self.lua.execute("collectgarbage('collect')")
			self.lua.execute("collectgarbage('setpause', 100)")
			self.lua.execute("collectgarbage('setstepmul', 5000)")

			self.lua.globals().PiniLuaHelper = GraphicsProtocolObject.LuaHelper()
			self.lua.execute("OnPreview=true")
			
			self.lua.execute("XVM = require('LXVM')")
			self.lua.execute("XVM:init()")
			self.lua.execute("AnimMgr = require('AnimMgr')")
			self.lua.execute("AnimMgr:clear()")
			self.lua.execute("AnimMgr:init(XVM)")
			self.lua.execute("PiniLib = require('PiniLib')")
			self.lua.execute("_AUTO_ = _AUTO_ or {}")

			self.lua.execute("require('FILEMANS')")
			self.lua.execute("libDef = require(FILES['module/libdef.lnx']:gsub('%.lua',''))")
			
			self.XVM = self.lua.globals().XVM
			self.PiniAPI = self.lua.globals().pini
			self.PiniLib = self.lua.globals().PiniLib
			self.libDef = self.lua.globals().libDef

			self.lua.globals().FAL_REGIST = ATL.FAL_REGIST
			self.lua.globals().FAL_GETFRAME = ATL.FAL_GETFRAME
			self.lua.globals().FAL_GETVALUE = ATL.FAL_GETVALUE
			self.lua.globals().FAL_GETSTRVALUE = ATL.FAL_GETSTRVALUE
			self.lua.globals().FAL_ISVALUE = ATL.FAL_ISVALUE
			self.lua.globals().FAL_DELETEFRAME = ATL.FAL_DELETEFRAME
			self.lua.globals().FAL_MAXFRAME = ATL.FAL_MAXFRAME
			self.lua.globals().FAL_MARKEDFRAMES = ATL.FAL_MARKEDFRAMES
			self.lua.globals().FAL_ISEXISTS = ATL.FAL_ISEXISTS
			self.lua.globals().FAL_NUMNODE = ATL.FAL_NUMNODE
			self.lua.globals().FAL_REGISTSTRINGVALUE = ATL.FAL_REGISTSTRINGVALUE
			self.lua.globals().FAL_REGISTNUMBERVALUE = ATL.FAL_REGISTNUMBERVALUE
			self.lua.globals().FAL_DELETENODEVALUE = ATL.FAL_DELETENODEVALUE
			self.lua.globals().FAL_CLEARFRAME = ATL.FAL_CLEARFRAME

			self.clear()

		except Exception, e:
			fp = QFile("errorout.txt")
			fp.open(QIODevice.WriteOnly | QIODevice.Text)
			
			out = QTextStream(fp)
			out.setCodec("UTF-8")
			out.setGenerateByteOrderMark(False)
			out<<e.message

			out = None
			fp.close()

			QTimer.singleShot(1000, self.luaInit)

	def XLSXClear(self):
		try:
			self.lua.execute("XLSX_CLEAR()")
		except Exception, e:
			print e

	def RefreshBuildPath(self):
		try:
			self.lua.execute("REFRESH_BUILD_PATH()")
		except Exception, e:
			print e

	def clear(self):
		if self.XVM == None:
			return 

		projCtrl = ProjectController()
		self.RefreshBuildPath()
		
		self.showDialog = False

		self.lua.execute("package.loaded['FILEMANS'] = nil")
		self.lua.execute("FILES = nil")
		self.lua.execute("require('FILEMANS')")

		self.lua.execute("_G._LOG_ = {}")
		self.Logs = self.lua.globals()._LOG_
		
		self.lua.globals().WIN_WIDTH     = projCtrl.screenWidth
		self.lua.globals().WIN_HEIGHT    = projCtrl.screenHeight
		self.lua.globals().PiniLuaHelper = GraphicsProtocolObject.LuaHelper()

		self.XVM.init(self.XVM)
		self.PiniAPI.Clear(self.PiniAPI)
		self.libDef(self.XVM)
		self.PiniLib(self.XVM)
		self.Display = self.PiniAPI._regist_.Display
		self.addIndex = 1

	def insert(self,compiled):
		if self.XVM == None:
			return 

		if compiled and len(compiled) > 0 :
			compiled = "fname=" + str(self.addIndex) + "\n" + compiled
			self.addIndex = self.addIndex + 1
			self.lua.execute(compiled)

	def display(self):
		if self.XVM == None:
			return 

		if self.sceneCtrl == None :
			return 

		projCtrl = ProjectController()
		self.attachNode = []
		self.errorLog = []
		
		dialog = None
		if self.showDialog : 
			try:
				dialog = self.lua.globals().pini.Dialog
				dialog.Preview(dialog)
				dialog.showAllLetters(dialog)
			except Exception, e:
				print "************************************"
				print e
				print "************************************"
				traceback.print_exc(file=sys.stdout)

		nodes = {}
		for k,v in sorted(self.Display.items(),key=lambda obj: obj[1].drawOrder ) : 
			if v.visible : 
				node = None
				if v.type == "Node" :
					node = GraphicsProtocolObject.Node(v)
				elif v.type == "Sprite" : 
					src = os.path.join(projCtrl.path,"image",v.path)
					if QFile(src).exists() : 
						node = GraphicsProtocolObject.Image(v)
					else :
						self.errorLog.append(v.path)

				elif v.type == "ColorLayer" :
					node = GraphicsProtocolObject.ColorLayer(v)
				elif v.type == "Label" :
					node = GraphicsProtocolObject.Label(v)
				elif v.type == "TextInput":
					v.text = v.holder
					node = GraphicsProtocolObject.Label(v)
				elif v.type == "Slider" : 
					src1 = os.path.join(projCtrl.path,"image",v.img1)
					src2 = os.path.join(projCtrl.path,"image",v.img2)
					src3 = os.path.join(projCtrl.path,"image",v.img3)
					c = QFile(src1).exists() and QFile(src2).exists() and QFile(src3).exists()
					if c : 
						node = GraphicsProtocolObject.Slider(v)
					else :
						self.errorLog.append(v.img1)
						self.errorLog.append(v.img2)
						self.errorLog.append(v.img3)

				if node:
					size = node.boundingRect()
					#ancX = (v.anchorX-0.5) * size.width()
					#ancY = (v.anchorY-0.5) * size.height()

					#pos = node.pos()
					#node.setPos(pos.x() - ancX, pos.y() - ancY)

				nodes[v.id] = node
				if node:
					node.setZValue(v.zOrder)
					if v.parent and v.parent.id in nodes :
						node.setParentItem(nodes[v.parent.id])
					else:
						self.attachNode.append(node)
						#self.sceneCtrl.view.scene.addItem(node)

		if dialog : 
			dialog.Reset(dialog)
			dialog.UseConfig(dialog,None)

		ATL.FAL_CLEARFRAME()
		#self.sceneCtrl.view.update()
		#self.sceneCtrl.view.fitInView()

	def updateFuncsInfo(self) :
		if self.XVM == None:
			return 

		lua = self.lua.globals()
		self.funcsInfo = lua._LNXFucInfo

	def getFuncInfo(self):
		if self.funcsInfo == None : 
			self.libDef(self.XVM)
			self.updateFuncsInfo()
		return self.funcsInfo

	def build(self,sceneCtrl):
		if self.XVM == None:
			return 

		self.sceneCtrl = sceneCtrl
		try:
			for i in range(1, self.addIndex):
				self.XVM.call(self.XVM,i)

			lnxf = self.lua.globals()._LNXF
			self.showDialog = False
			if lnxf[self.addIndex - 1] != None:
				if lnxf[self.addIndex - 1]()[2] != None:
					if lnxf[self.addIndex - 1]()[2]["t"] == 12:
						self.showDialog = True

			self.display()
		except Exception, e:
			print "error>>",e
			traceback.print_exc(file=sys.stdout)

def connectMarkupCompletion(editor):
	editor.completionShow(QStringListModel(editor.bookmarkList()))

def fontMarkupCompletion(editor):
	fontList = []
	for k,v in FontManager().fonts.iteritems():
		if (k == "NanumGothicCoding"):
			continue
		fontList.append(k)
	editor.completionShow(QStringListModel(fontList))

class ScriptMarkup(QObject):
	markups = [
		[u"색상"," 0 0 0",True,None],
		[u"클릭","",False,None],
		[u"비활성","",False,None],
		[u"크기"," 30",True,None],
		[u"자간"," 30",False,None],
		[u"행간"," 20",False,None],
		[u"공백"," 0",False,None],
		[u"연결"," \"\"",True,connectMarkupCompletion],
		[u"대기"," 1",False,None],
		[u"시간"," 0.02",False,None],
		[u"폰트"," \"\"",True,fontMarkupCompletion],
		[u"클린","",False,None],
		[u"닫기","",False,None],
		[u"켜기","",False,None],
		[u"=","",False,None]
	]

	@staticmethod
	def Markup():
		return [ v[0] for v in ScriptMarkup.markups ]

	@staticmethod
	def MarkupCompletion(editor,text,origTc):
		marks = [ v for v in ScriptMarkup.markups if v[0] == text ]
		if len(marks) == 1:
			mark = marks[0]
			tc = QTextCursor(origTc)
			tc.insertText(text)
			tc.insertText(mark[1])

			if mark[2] :
				tc.movePosition(QTextCursor.Right)
				text = "</"+mark[0]+">"
				tc.insertText(text)
				tc.movePosition(QTextCursor.Left,QTextCursor.MoveAnchor,len(text))

			mc = len(mark[1])-1
			tc.movePosition(QTextCursor.Left,QTextCursor.MoveAnchor,mc if mc > 0 else 0 )

			tc.select(QTextCursor.WordUnderCursor)
			t = tc.selectedText()
			if not t.startswith("\"\"") and not t.startswith("<=") : 
				editor.setTextCursor(tc)

			if mark[3] : 
				mark[3](editor)

class ScriptCommand(QObject):
	ToolChain = LNXToolChain()

	def __init__(self,text):
		super(ScriptCommand,self).__init__(None)

	@staticmethod
	def ExistsFunc(name):
		funcs = ScriptGraphicsProtocol().getFuncInfo()
		try:
			return name in funcs
		except Exception, e:
			print e
			return False

	@staticmethod
	def List():
		funcs = ScriptGraphicsProtocol().getFuncInfo()

		def mySorted(a):
			# print "a=",a
			# print "a[1][\"idx\"]=",a[1]["idx"]
			return a[1]["idx"]

		funcs = sorted(funcs.items(),key=mySorted)

		cmds = [ k for k,v in funcs ]
		expl = [ v["default"] if "default" in v else "" for k,v in funcs ]

		return [cmds,expl]

	@staticmethod
	def GetReferenceUrl(cmd):
		funcs = ScriptGraphicsProtocol().getFuncInfo()

		def mySorted(a):
			return a[1]["idx"]

		funcs = sorted(funcs.items(),key=mySorted)
	
		for k,v in funcs:
			if k == cmd:
				expl = v["default"]
				index = string.find(expl, "a href=")
				if index != -1:
					endIndex = string.find(expl, "'", index+8)
					return expl[index+8:endIndex]
		return None

	@staticmethod
	def GetExplain(cmd):
		funcs = ScriptGraphicsProtocol().getFuncInfo()

		def mySorted(a):
			return a[1]["idx"]

		funcs = sorted(funcs.items(),key=mySorted)
	
		for k,v in funcs:
			if k == cmd:
				return v["default"]
		return None

	@staticmethod
	def GetExplainArg(cmd,arg):
		inf = ScriptGraphicsProtocol().getFuncInfo()[cmd]
		lua = ScriptGraphicsProtocol().lua.globals()

		if inf : 
			exps = []
			if inf["extens"] :
				lists = sorted(inf["extens"].items())
				exps = exps+[v[3] if len(v) >= 3 else "" for k,v in lists if k == arg] 
			if inf["explain"] : 
				lists = sorted(inf["explain"].items())
				exps = exps+[v[3] if len(v) >= 3 else "" for k,v in lists if k == arg] 
				
			if len(exps) > 0:
				return exps[0]
		return None

	@staticmethod
	def GenObjLine(text):
		if text == "\t":
			return None

		if len(text) > 0:
			s,obj = ScriptCommand.ToolChain.gen_obj(text,True)

			if obj:
				return obj
			return False
		return None

	@staticmethod
	def CompileLine(text):
		if  text == "\t" : 
			return None
			
		if len(text) > 0 :
			s,obj = ScriptCommand.ToolChain.gen_obj(text,True)
			if obj :
				return [ScriptCommand.ToolChain.gen_lua_line(obj),obj] 
			elif obj == False:
				return False
		return None

	@staticmethod
	def Selected(editor,text,cursor):
		inf = ScriptGraphicsProtocol().getFuncInfo()[text]
		if inf : 
			if inf["extens"] : 
				for k,v in sorted(inf["extens"].items()) : 
					default = ScriptCommand.ArgDefault(text,k)
					if default == "None" :
						default = "\"\""

					editor.insertText(" "+k+"="+default)
				editor.insertText(" ")

			cmd,pos = editor.currentCommand()
			if len(cmd) == 0 :
				return 
			
			cursor.setPosition(pos)

			editor.setTextCursor(cursor)
			editor.nextArg(cmd,pos)

	@staticmethod
	def ArgDefault(cmd,arg):
		lua = ScriptGraphicsProtocol().lua.globals()
		inf = ScriptGraphicsProtocol().getFuncInfo()[cmd]
		v = None
		if inf["extens"] and inf["extens"][arg] : 
			v = inf["extens"][arg]
		elif inf["explain"] and inf["explain"][arg] :
			v = inf["explain"][arg]
		if v:
			if v[2] == None :
				return '""'
			if type(v[2]) == types.UnicodeType:
				return '"'+v[2]+'"' 
			else:
				return str(v[2]) 
		return '""'

	@staticmethod
	def ArgSuggestList(cmd,arg):
		lua = ScriptGraphicsProtocol().lua.globals()
		inf = ScriptGraphicsProtocol().getFuncInfo()[cmd]

		v = None
		if inf["extens"] and inf["extens"][arg] : 
			v = inf["extens"][arg]
		elif inf["explain"] and inf["explain"][arg] :
			v = inf["explain"][arg]
		if v:
			lists = lua._AUTO_[v[1]]
			if lists:
				s = 0
				try:
					s = 0 if type(lists[0][0]) != types.NoneType else 1
				except Exception, e:
					s = 0 if type(lists[1][0]) != types.NoneType else 1
				
				try:
					return [a[s] for a in lists], [a[s+1] for a in lists]
				except Exception, e:
					try:
						return [lists[a][s] for a in lists], [lists[a][s+1] for a in lists]
					except Exception, e:
						print e
						traceback.print_exc(file=sys.stdout)
		return [],[]

	@staticmethod
	def UpdateSuggestArgument():
		from view.AssetLibraryWindow import AssetLibraryWindow

		lua = ScriptGraphicsProtocol().lua.globals()
		a = lua._AUTO_

		img_path = ProjectController().path + QDir.separator() + "image" + QDir.separator()
		sound_path = ProjectController().path + QDir.separator() + "sound" + QDir.separator()

		_fi_sound= [v.replace(sound_path,"").replace("\\","/") for v in AssetLibraryWindow().audio ]
		_fi_imgs = [v.replace(img_path,"").replace("\\","/") for v in AssetLibraryWindow().images ]
		_fi_fonts= [v.replace(img_path,"").replace("\\","/") for v in FontManager().fonts ]
		_fi_fonts.remove("NanumGothicCoding")

		_id_node = [v.id for k,v in sorted(lua.pini._regist_.Display.items()) ]
		_id_sound = [k for k,v in sorted(lua.pini._regist_.Sounds.items()) ]
		_id_timer = [k for k,v in sorted(lua.pini._regist_.Timers.items()) if k[:4] != "PINI"]
		_id_ineff = [k for k,v in sorted(lua.fs_imageEffect.items()) ]
		_id_outef = [k for k,v in sorted(lua.fs_imageDeleteEffect.items()) ]
		_id_anim = [k for k,v in sorted(lua.fs_animation.items()) ]

		_id_size = [k for k,v in sorted(lua.fs_size.items()) ]
		_id_pos = [k for k,v in sorted(lua.fs_position.items()) ]
		
		imgurl=["img://"+v.replace("\\","/") for v in AssetLibraryWindow().images ]

		a[u"노드아이디"] = zip(_id_node,[u"현재 화면에 출력되고 있는 오브젝트의 아이디"]*len(_id_node))
		a[u"사운드아이디"] = zip(_id_sound,[u"현재 출력되고 있는 사운드의 아이디"]*len(_id_sound))
		a[u"타이머아이디"] = zip(_id_timer,[u"현재 실행되고 있는 타이머의 아이디"]*len(_id_timer))
		a[u"노드입장효과"] = zip(_id_ineff,[u"노드 입장효과.. 정리해야함. TODO "]*len(_id_ineff))
		a[u"노드퇴장효과"] = zip(_id_outef,[u"노드 퇴장효과.. 정리해야함. TODO "]*len(_id_outef))
		a[u"애니메이션타입"] = zip(_id_anim,[u"애니메이션 타입.. 정리해야함. TODO "]*len(_id_anim))
		
		a[u"크기"] = zip(_id_size,[u"크기들.. 정리해야함. TODO"]*len(_id_size))
		a[u"위치"] = zip(_id_pos,[u"위치들.. 정리해야함. TODO"]*len(_id_pos))

		a[u"폰트파일"] = zip(_fi_fonts,[u"이 텍스트를 표기할 폰트"]*len(_fi_fonts))

		a[u"이미지파일"] = zip(_fi_imgs,imgurl)
		a[u"사운드파일"] = zip(_fi_sound,[""]*len(_fi_sound))
		
		cmds, expl = ScriptCommand.List()
		a[u"함수목록"] = zip(cmds, expl)

	@staticmethod
	def Step(editor,cmd,argName):
		ScriptCommand.UpdateSuggestArgument()
		ScriptCommand.editor = editor
		ScriptCommand.suggested_cmd = cmd
		ScriptCommand.suggested_argName = argName
		
		if len(cmd) == 0 : 
			cmd,pos = editor.currentCommand()

		if len(cmd) == 0 : 
			return False;

		arr1,arr2 = ScriptCommand.ArgSuggestList(cmd,argName)

		editor.completionClose()
		editor.completionShow(QStringListModel(arr1),ScriptCommand.SelectArgument,arr2)

		return True;

	@staticmethod
	def SelectArgument(text,tc):
		editor = ScriptCommand.editor 
		cmd = ScriptCommand.suggested_cmd
		argName = ScriptCommand.suggested_argName

		if cmd == u"루아" : 
			pass
		elif cmd == u"애니메이션" and argName == u"타입" :
			editor.currentArg(cmd,None)
			tc.removeSelectedText()
			tc.insertText(text)

			tc.movePosition(QTextCursor.Right,QTextCursor.MoveAnchor,1)
			endtc = editor.findLine("]")
			if endtc : 
				e = endtc.position() - tc.position() - 1
				if e > 0 :
					tc.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor,e)
			lua = ScriptGraphicsProtocol().lua.globals()
			tc.insertText(" "+lua.fs_animation[text][1]+" ") 
		else:
			s = None
			e = None
			s1 = editor.findLine("\"",QTextDocument.FindBackward)
			s2 = editor.findLine("=",QTextDocument.FindBackward)
			if s1.position() > s2.position() : 
				s = s1
				e = editor.findLine("\"")
			else:
				s = s2
				e = editor.findLine(" ")

			s.clearSelection()

			s.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor,e.position()-s.position() - 1)
			s.insertText(text)

	@staticmethod
	def CanInsertArgs(cmd, ignores):
		inf = ScriptGraphicsProtocol().getFuncInfo()[cmd]
		lua = ScriptGraphicsProtocol().lua.globals()

		if inf : 
			cmds = []
			exps = []
			if inf["extens"] :
				lists = sorted(inf["extens"].items())
				cmds = cmds+[k for k,v in lists if not k in ignores]
				exps = exps+[v[3] if len(v) >= 3 else "" for k,v in lists if not k in ignores] 
			if inf["explain"] : 
				lists = sorted(inf["explain"].items())
				cmds = cmds+[k for k,v in lists if not k in ignores]
				exps = exps+[v[3] if len(v) >= 3 else "" for k,v in lists if not k in ignores] 
		return cmds,exps

	@staticmethod
	def Enter(editor,strs):
		pass
