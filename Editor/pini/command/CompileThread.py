# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from PySide.QtGui import * 
from PySide.QtCore import *

import threading
from Queue import Queue

import traceback
import os
import json

from command.ScriptCommands import ScriptGraphicsProtocol
from controller.ProjectController import ProjectController

class ComplieThread(QThread):
	# 프리뷰에 표기하기 위해 미리 컴파일된 코드를 실행하는 스레드입니다.
	def __init__(self, scene, previewNum, compiled , parent = None ):
		QThread.__init__(self, parent)
		self.previewBlockNumber = previewNum
		self.compiledCommand = compiled
		self.sceneCtrl = scene

	def run(self):
		try:
			isdebug = False
			if self.sceneCtrl :
				protocol = ScriptGraphicsProtocol()
				#protocol.clear()
				
				num = self.previewBlockNumber

				while len(self.compiledCommand) <= num:
					# 아직 컴파일이 덜 되었으므로, 기다립니다.
					self.msleep(50)

				curCmd = self.compiledCommand[num]
				curBlock = False
				
				if isdebug : 
					print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"

				if curCmd["isInBlock"] :
					curBlock = curCmd["blockIdx"]

				_usedBlock = []
				_usedSemi  = []
				for i in range(0,num+1):
					cmd = self.compiledCommand[i]
					compiled = cmd["compiled"]
					if compiled : 
						if (not curBlock) and cmd["isInBlock"] : 
							continue
						if curBlock:
							if not cmd["isInBlock"]:
								continue

						if (curBlock != False) and curBlock != cmd["blockIdx"]:
							continue

						if curBlock != cmd["blockIdx"]:
							if cmd["blockIdx"] in _usedBlock : 
								continue
							_usedBlock.append(cmd["blockIdx"])

						protocol.insert(compiled[0])
						if isdebug : 
							print ">", compiled[0]

				protocol.build(self.sceneCtrl)
		except Exception, e:
			traceback.print_exc(file=sys.stdout)
			print ">>ComplieThread",e

class CompilingThread(QThread):
	# 프리뷰에 표기하기 위한 목적의 컴파일 스레드입니다.
	beginBusy = Signal(bool)
	completeCallback = Signal(list)

	def __init__(self, editor,parent = None ):
		QThread.__init__(self, parent)
		self.compileQueue = Queue() # Python Queue 는 Thread-safe 하므로, 별도의 크리티컬 영역 관리는 없습니다.
		self.isBusy = False
		self.editor= editor
		self.toDestroy = False

	def enqueueCompile(self,update,callback=None,line = -1,lineRange = -1):
		self.compileQueue.put([update,callback,line,lineRange])

	def doDestroy(self):
		self.toDestroy = True

	def run(self):
		self.toDestroy = False

		while not self.toDestroy:
			self.msleep(50)
			try:
				try:
					task = self.compileQueue.get(False)
				except Exception, e:
					if self.isBusy:
						self.beginBusy.emit(False)
					self.isBusy = False
					continue

				if not self.isBusy:
					self.beginBusy.emit(True)
				self.isBusy = True
				isdebug = False

				update = task[0]
				callback = task[1]
				line = task[2]
				lineRange = task[3]

				if line == -1 and lineRange == -1:
					self.editor.compiledCommand = []
					for i in range(0,self.editor.blockCount()):
						self.editor.compileBlockNumber(i,update)
				elif lineRange != -1:
					for i in range(0,lineRange):
						self.editor.compileBlockNumber(line+i,update)
				else:
					self.editor.compileBlockNumber(line,update)

				if callback != None:
					self.completeCallback.emit([callback])

				self.compileQueue.task_done()

			except Exception, e:
				print " >>CompilingThread",e
				traceback.print_exc(file=sys.stdout)
				print " <<CompilingThread",e

class TempSaveThread(QThread):
	# 임시저장을 위한 스레드입니다.
	def __init__(self, fileName, text, parent = None ):
		QThread.__init__(self, parent)
		self.fileName = fileName
		self.text = text

	def run(self):
		PROJPATH = ProjectController().path

		tempDir = "tempSave"
		fp = None

		if not os.path.exists(os.path.join(".",tempDir)):
			os.mkdir(os.path.join(".",tempDir))

			tmp_proj_path = os.path.join(".",tempDir,"PROJ")

			if not os.path.exists(tmp_proj_path):
				fp = QFile(tmp_proj_path)

				DAT = { "PROJ" : PROJPATH }

				fp.open(QIODevice.WriteOnly | QIODevice.Text)
				out = QTextStream(fp)
				out.setCodec("UTF-8")
				out.setGenerateByteOrderMark(False)
				out << json.dumps(DAT)
				out = None
				fp.close()

				fp = None

		tmp_path_1 = os.path.join(".",tempDir,self.fileName)
		tmp_path_2 = os.path.join(".",tempDir,self.fileName+"_b")

		saveSub = False
		if os.path.exists( tmp_path_1 ) : 
			saveSub = True

		if saveSub : 
			fp = QFile(tmp_path_2)
		else:
			fp = QFile(tmp_path_1)

		DAT = { "PLAIN": self.text }

		fp.open(QIODevice.WriteOnly | QIODevice.Text)
		out = QTextStream(fp)
		out.setCodec("UTF-8")
		out.setGenerateByteOrderMark(False)
		out << json.dumps(DAT)
		out = None
		fp.close()

		fp = None

		if saveSub : 
			os.remove(tmp_path_1)
			os.rename(tmp_path_2,tmp_path_1)