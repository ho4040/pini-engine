# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import os
import json
import hashlib
import base64

import shutil
import compiler
from slpp import slpp
import json
from Queue import Queue

import os_encoding
import traceback

from openpyxl import load_workbook

from PySide.QtCore import *
from PySide.QtGui import *

import codecs

class ProjectController(QObject):
	class ProjectModel(QObject):pass
	#signal
	changed = Signal(unicode)

	_instance = None
	_isInit   = False
	def __new__(cls, *args, **kwargs):
		if not ProjectController._instance:
			ProjectController._instance = super(ProjectController,cls).__new__(cls,*args,**kwargs)

		return ProjectController._instance

	def __init__(self,src=None,parent=None):
		if ProjectController._isInit:
			return 
		ProjectController._isInit = True

		super(ProjectController,self).__init__()
		self._path = ""
		self.projectInfoLoaded = False
		self._screenWidth = 960
		self._screenHeight = 640
		self._fullscreen = False

		self.workerController = WorkerController()

	def loadProj(self):
		PROJPATH = self._path
		PROJFILE = PROJPATH + "/PROJ"
		DEFFILE = PROJPATH + "/DEFINESET"

		def fileOpen(fileName):
			fp = QFile(fileName)
			fp.open(QIODevice.ReadOnly | QIODevice.Text)

			fin = QTextStream(fp)
			fin.setCodec("UTF-8")
			FILEDATA = fin.readAll()
			fin = None
			fp.close()

			return FILEDATA

		_d = json.loads(fileOpen(PROJFILE))

		self._screenWidth = 800
		self._screenHeight = 600
		self._fullscreen = False
		self._orientation = False
		
		try:
			self._screenWidth = _d["width"]
		except Exception, e:
			pass
		try:
			self._screenHeight = _d["height"]
		except Exception, e:
			pass
		try:
			self._fullscreen = _d["fullscreen"]
		except Exception, e:
			pass
		try:
			self._orientation = _d["orientation"]
		except Exception, e:
			pass

		self._defines = []

		try:
			_d = json.loads(fileOpen(DEFFILE))

			self._defines = _d["defines"]
		except Exception, e:
			pass

	def projectInfoSave(self):
		PROJPATH = self._path
		PROJECT_INFO = {
			"width":self._screenWidth,
			"height":self._screenHeight,
			"fullscreen":self._fullscreen,
			"orientation":self._orientation,
		}
		
		fp = QFile(PROJPATH + "/PROJ")
		fp.open(QIODevice.WriteOnly | QIODevice.Text)

		out = QTextStream(fp)
		out.setCodec("UTF-8")
		out.setGenerateByteOrderMark(False)
		out << json.dumps(PROJECT_INFO)
		out = None
		fp.close()

		DEFINE_INFO = {
			"defines":self._defines,
		}

		fp = QFile(PROJPATH + "/DEFINESET")
		fp.open(QIODevice.WriteOnly | QIODevice.Text)

		out = QTextStream(fp)
		out.setCodec("UTF-8")
		out.setGenerateByteOrderMark(False)
		out << json.dumps(DEFINE_INFO)
		out = None
		fp.close()

	def setRebuildFlag(self):
		PROJPATH   = self._path
		BUILDPATH  = PROJPATH + "/build/"
		checks = {}
		fpath = BUILDPATH+"o"

		fp = QFile(fpath)
		fp.open(QIODevice.WriteOnly | QIODevice.Text)
			
		out = QTextStream(fp)
		out.setCodec("UTF-8")
		out.setGenerateByteOrderMark(False)
		out << json.dumps(checks)

		out = None
		fp.close()

	def compileProj(self,isPrecompile=False,callback=None,callbackInst=False):
		if isPrecompile:
			self.compileProjWork(True)
		else:
			self.workerController.enqueueWork(self.compileProjWork,callback,callbackInst)

	def workerDone(self):
		pass

	def compileProjWork(self,isPrecompile=False):
		ERROR_LNXS = []
		PROJPATH   = self._path
		SCENEPATH  = PROJPATH + "/scene/"
		MODULEPATH = PROJPATH + "/module/"
		BUILDPATH  = PROJPATH + "/build/"
		OBJECTPATH = PROJPATH + "/build/obj/"
		BUILDMODULEPATH = PROJPATH + "/build/module/"
		
		#if not os.path.exists(BUILDMODULEPATH):
		#	os.makedirs(BUILDMODULEPATH)
		
		################################################
		######## complie all scene! ####################
		################################################
		def readAll(fpath):
			fp = QFile(fpath)
			fp.open(QIODevice.ReadOnly | QIODevice.Text)

			fin = QTextStream(fp)
			fin.setCodec("UTF-8")

			text = fin.readAll()

			fin = None
			fp.close()

			return text

		def save(fpath,table):
			fp = QFile(fpath)
			fp.open(QIODevice.WriteOnly | QIODevice.Text)
				
			out = QTextStream(fp)
			out.setCodec("UTF-8")
			out.setGenerateByteOrderMark(False)
			out << json.dumps(table)

			out = None
			fp.close()

		def JSON(text):
			return json.loads(text)

		def checksum(fpath):
			return base64.b64encode(hashlib.md5(open(fpath, 'rb').read()).digest())

		def fileNameMD(fname):
			fname.encode(os_encoding.cp())
			return base64.encodestring(fname.encode(os_encoding.cp())).replace("\n","").replace("=","_").replace("+","_0_").replace("/","__0")
	
		def getV(v):
			ret = unicode( "", "utf-8")	
			if v != None:
				if isinstance(v, unicode)==False:
					ret = str(v)
					ret = unicode(ret, "utf-8")
				else:
					ret = v
			return  ret

		def findWordInCompiledObject(o,marge):
			for v in o : 
			 	if v["t"] == 12 : 
			 		for w in v["strs"] : 
			 			marge[w] = marge.get(w, 0) + 1

		DEFAULT_PROJ_RES = u"resource/proj_default"
		for root, dirs, files in os.walk(DEFAULT_PROJ_RES, topdown=False):
			for name in files:
				fullpath = os.path.join(root, name)
				dstDir = PROJPATH + root.replace(DEFAULT_PROJ_RES,"") + "\\"
				dst = dstDir + name

				if name == u"libdef.lnx" : 
					if checksum(fullpath) != checksum(dst) : 
						try:
							os.remove(dst)
						except Exception, e:
							pass
						shutil.copyfile(fullpath,dst)
				elif name == "TMP" : 
					pass
				else:
					if not os.path.exists(dst):
						try:
							if not os.path.exists(dstDir):
								os.makedirs(dstDir)
						except Exception, e:
							pass
						shutil.copyfile(fullpath,dst)
						
		compilerVersion = ""
		try:
			versionDir = os.path.join("..","pini_ver.inf")
			compilerVersion = readAll(versionDir)
		except Exception, e:
			pass

		checks = {}
		fileMans = {}
		imgMans = {}
		words = {}
		try:
			checks = JSON(readAll(BUILDPATH+"o"))

			if not "compilerVersion" in checks:
				checks = {}
			elif checks["compilerVersion"] != compilerVersion:
				checks = {}
		except Exception, e:
			pass

		checks["compilerVersion"] = compilerVersion

		luaToolChain = None

		from view.CompileProgressWindow import CompileProgressWindow

		BPATH = BUILDPATH.replace("\\","/")
		PPATH = PROJPATH.replace("\\","/")
		for root, dirs, files in os.walk(PROJPATH, topdown=False):
			_root = root.replace("\\","/")
			for name in files:
				if _root == PPATH or (_root+"/").startswith(BPATH) : 
					continue

				if _root.endswith("/keystore") :
					continue

				fullpath = os.path.join(root, name)
				relative = root.replace(PROJPATH,"")
				extension= os.path.splitext(name)

				skipflag = False
				for dirName in relative.replace("\\","/").split("/"):
					if len(dirName) > 0 and dirName[0] == ".":
						skipflag = True
						break
				if skipflag:
					continue
				
				ID = relative+"/"+extension[0]+extension[1]
				relative  = relative.replace("\\","/")
				relatives = relative.split("/")

				relative  = os.path.join(*relatives[0:2])
				relatives = relatives[2:]
				for v in relatives : 
					relative = os.path.join(relative,fileNameMD(v))

				distPath = (BUILDPATH+relative).replace("\\","/")

				if not os.path.exists(distPath):
					os.makedirs(distPath)

				if extension[1] == ".lnx" : 
					dist = distPath+"/"+"lnx_"+fileNameMD(extension[0])+".lua"
				else:
					dist = distPath+"/"+fileNameMD(extension[0])+extension[1]

				dist = dist.replace("\\","/")
				
				fileID = ID[1:] if ID.startswith("\\") or ID.startswith("/") else ID
				fileID = fileID.replace("\\","/")
				fileMans[fileID] = dist.replace(BPATH,"")

				if extension[1] in [".jpg",".png",".jpeg"] : 
					img = QImage(fullpath)
					imgMans[fileID] = {"w":img.size().width(),"h":img.size().height()};

				if ID in checks : 
					try:
						if checks[ID] == checksum(fullpath) : 
							continue
					except Exception, e:
						continue
					
				######### file compile! #########
				if extension[1] == ".lnx" : 
					errLine = -1
					if luaToolChain == None : 
						luaToolChain = compiler.LNXToolChain()
					if name == "libdef.lnx" or (not isPrecompile):
						# print "compile!" , fullpath
						CompileProgressWindow(None).setText(u"컴파일 중 - " + name)
						l,o,errLine = luaToolChain.compileFile(fullpath,dist,name != "libdef.lnx")
					else:
						o = "[]"

					if o != None : 
						distPath = OBJECTPATH+relative
						if not os.path.exists(distPath):
							os.makedirs(distPath)
						
						dist = distPath+"/"+extension[0]+".obj"

						with codecs.open(dist, "w", "utf-8") as fp : 
							fp.write(json.dumps(o))
						# fp = QFile(dist)
						# fp.open(QIODevice.WriteOnly | QIODevice.Text)
						
						# out = QTextStream(fp)
						# out.setCodec("UTF-8")
						# out.setGenerateByteOrderMark(False)
						# out << json.dumps(o)

						# out = None
						# fp.close()

						findWordInCompiledObject(o,words)

					else:
						ERROR_LNXS.append([extension[0],errLine])
						continue
				elif extension[1] == ".xlsx" :
					if extension[0].startswith("~$") :
						pass
					else:
						try:
							if os.access(fullpath, os.R_OK):
								table = {}
								
								if not isPrecompile:
									wb = load_workbook(fullpath)
									table["primary"] = ""
									for sheet in wb : 
										table[sheet.title] = {}
										if len(table["primary"]) == 0 : 
											table["primary"] = sheet.title
										row_count = 0
										for row in sheet.rows:
											row_table = {}
											col_count = 0
											for cell in row:
												if cell.value != None : 
													row_table[unicode(col_count)] = getV(cell.value)
												col_count = col_count+1
											if len(row_table) > 0 : 
												table[sheet.title][unicode(row_count)] = row_table
											row_count = row_count+1

								with codecs.open(dist, "w", "utf-8") as fp : 
									fp.write(json.dumps(table, ensure_ascii=False,encoding="utf-8"))

								# fp = QFile(dist)
								# fp.open(QIODevice.WriteOnly | QIODevice.Text)

								# out = QTextStream(fp)
								# out.setCodec("UTF-8")
								# out.setGenerateByteOrderMark(False)
								# out << json.dumps(table, ensure_ascii=False,encoding="utf-8")
								# out = None
								# fp.close()
								# wb = None

							#shutil.copyfile(fullpath,dist)
						except Exception, e:
							traceback.print_exc(file=sys.stdout)
				else:
					try:
						shutil.copyfile(fullpath,dist)
					except Exception, e:
						print e
				try:
					checks[ID] = checksum(fullpath)
				except Exception, e:
					pass

		if not isPrecompile:
			#print checks
			save(BUILDPATH+"o",checks)

		#project info
		PROJECT_INFO = {"width":self._screenWidth,"height":self._screenHeight,"fullscreen":self._fullscreen}
		with codecs.open(BUILDPATH+"ProjectInfo.lua", "w", "utf-8") as fp : 
			fp.write("return "+slpp.encode(PROJECT_INFO)+"\n")

		# fp = QFile(BUILDPATH+"ProjectInfo.lua")
		# fp.open(QIODevice.WriteOnly | QIODevice.Text)

		# out = QTextStream(fp)
		# out.setCodec("UTF-8")
		# out.setGenerateByteOrderMark(False)
		# out<<"return "<<slpp.encode(PROJECT_INFO)<<"\n"
		# out = None
		# fp.close()

		#FILEMANGER
		with codecs.open(BUILDPATH+"FILEMANS.lua", "w", "utf-8") as fp : 
			fp.write("FILES = {}\n")
			for k,v in fileMans.iteritems() :
				fp.write("FILES[\""+k+"\"]=\""+v+"\"\n")

		# fp = QFile(BUILDPATH+"FILEMANS.lua")
		# fp.open(QIODevice.WriteOnly | QIODevice.Text)

		# out = QTextStream(fp)
		# out.setCodec("UTF-8")
		# out.setGenerateByteOrderMark(False)
		# out<<"FILES = {}\n"
		# for k,v in fileMans.iteritems() :
		# 	out<<"FILES[\""+k+"\"]=\""+v+"\"\n"

		# out = None
		# fp.close()

		#IMAGEMANAGER
		with codecs.open(BUILDPATH+"IMGMANS.lua", "w", "utf-8") as fp : 
			fp.write("IMAGES = {}\n")
			for k,v in imgMans.iteritems() :
				fp.write("IMAGES[\""+k+"\"]="+slpp.encode(v)+"\n")

		# fp = QFile(BUILDPATH+"IMGMANS.lua")
		# fp.open(QIODevice.WriteOnly | QIODevice.Text)

		# out = QTextStream(fp)
		# out.setCodec("UTF-8")
		# out.setGenerateByteOrderMark(False)
		# out<<"IMAGES = {}\n"
		# for k,v in imgMans.iteritems() :
		# 	out<<"IMAGES[\""+k+"\"]="<<slpp.encode(v)<<"\n"

		# out = None
		# fp.close()

		return ERROR_LNXS

	@property
	def path(self):
		return self._path

	@property
	def screenWidth(self):
		return self._screenWidth

	@property
	def screenHeight(self):
		return self._screenHeight

	@property
	def fullscreen(self):
		return self._fullscreen

	@property
	def orientation(self):
		return self._orientation

	@property
	def defines(self):
		return self._defines

	@screenWidth.setter
	def screenWidth(self,v):
		self._screenWidth = v
		if self.projectInfoLoaded :
			self.projectInfoSave()

	@screenHeight.setter
	def screenHeight(self,h):
		self._screenHeight = h
		if self.projectInfoLoaded :
			self.projectInfoSave()

	@fullscreen.setter
	def fullscreen(self,v):
		self._fullscreen = v
		if self.projectInfoLoaded :
			self.projectInfoSave()

	@orientation.setter
	def orientation(self,v):
		self._orientation = v
		if self.projectInfoLoaded :
			self.projectInfoSave()

	@path.setter
	def path(self,path):
		self._path = path
		self.projectInfoLoaded = True
		self.loadProj()
		self.compileProj()
		self.changed.emit(path)

	@defines.setter
	def defines(self,v):
		self._defines = v
		if self.projectInfoLoaded :
			self.projectInfoSave()
		
	@property
	def sceneDirectory(self):
		return self._path + QDir.separator() + "scene"

class WorkerController(QObject):

	def __init__(self):
		super(WorkerController,self).__init__()
		self.workQueue = Queue()
		self.isWorking = False
		self.currentThread = False

	def enqueueWork(self,work,callback,callbackInst):
		thread = WorkerThread(self,work,callback,callbackInst)
		thread.workFinished.connect(self.workFinished)
		self.workQueue.put(thread)

		if not self.isWorking:
			self.doWork()

	def terminate(self):
		if self.isWorking:
			self.currentThread.quit()
			self.currentThread.wait()

	def doWork(self):
		try:
			task = self.workQueue.get(False)
		except Exception, e:
			self.isWorking = False
			return

		self.isWorking = True
		self.currentThread = task
		task.start()

	def workFinished(self,results):
		callback = results[0]
		result = results[1]
		callbackInst = results[2]
		self.currentThread = None
		if callback != None:
			callback(result,callbackInst)

		self.doWork()

class WorkerThread(QThread):

	workFinished = Signal(list)

	def __init__(self, parent, work, callback, callbackInst):
		super(WorkerThread,self).__init__(parent)
		self.parent = parent
		self.work = work
		self.callback = callback
		self.callbackInst = callbackInst
		
	def run(self):
		result = None
		try:
			# print "__START WORK"
			result = self.work()
			# print "__END WORK"

		except Exception, e:
			print " >>WorkerThread",e
			traceback.print_exc(file=sys.stdout)
			result = str(e) + "\n" + traceback.format_exc()
			print " <<WorkerThread",e

		finally:
			self.workFinished.emit([self.callback,result,self.callbackInst])
