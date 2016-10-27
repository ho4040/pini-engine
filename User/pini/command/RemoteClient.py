# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from PySide.QtCore import *
from PySide.QtNetwork import *

import os
import shutil

import socket
import thread, time
import hashlib
import base64
import json

from controller.ProjectController import ProjectController
from command.ScriptCommands import ScriptGraphicsProtocol

from view.OutputWindow import OutputWindow 

class RemoteClient(QTcpSocket):
	_instance = None
	_isInit   = False
	
	def __new__(cls, *args, **kwargs):
		if RemoteClient._instance: 
			RemoteClient._disconnect_()

		if not RemoteClient._instance:
			RemoteClient._instance = super(RemoteClient,cls).__new__(cls,*args,**kwargs)

		return RemoteClient._instance

	def __init__(self,parent):
		if RemoteClient._isInit : 
			return 
		RemoteClient._isInit = True

		super(RemoteClient,self).__init__(parent)

		self.status = 0
		self.live = False

		self.clean = False

		self.order = None
		self.payloadSize = None
		self.payload = None
		self.playScene = None
		self.startLine = None

		self._connect_try = 3

		self.readyRead.connect(self.onRead)
		self.disconnected.connect(self.onDisconnect)
		self.connected.connect(self.onConnected)

	def _connect(self,ip,port,clean,count=3):
		if self.playScene == None:
			self.playScene = u"scene/메인.lnx";
		print "remoteclient._connect() => ",self.playScene
		
		self.HOST = ip
		self.PORT = port
		self.clean = clean
		self._connect_try = count

		self.status = 2

		if self.live : 
			QTimer.singleShot(100,self.run)
		else:
			self.tryCount=0
			QTimer.singleShot(100,self.TryConnect)

	def onConnected(self):
		self.live = True
		OutputWindow().notice(u"테스트 실행 연결.")
		self.run()

	def TryConnect(self):
		self.tryCount += 1
		if self.tryCount > self._connect_try : 
			OutputWindow().notice(u"테스터와의 연결이 실패하였습니다.")
			RemoteClient._disconnect_()
			return
			
		self.connectToHost(self.HOST,self.PORT);
		if self.waitForConnected(5000):
			pass
		else:
			self.live = False
			QTimer.singleShot(1500,self.TryConnect)
			OutputWindow().notice(u"연결중...")

	def checksum(self,fpath):
		return base64.b64encode(hashlib.md5(open(fpath, 'rb').read()).hexdigest())

	def OnRecved(self,order,size,payload):
		print "OnRecved(self,)",order,size,payload
		if order == "ulst" : 
			self.OnUpdateFiles(json.loads(str(payload)))
		elif order == "ufin":
			self.status = 0
		elif order == "PATH" : 
			self.remote_writable_path = str(payload)
			if self.clean : 
				self.ClearRemoteDist()
			self.SendFileList()

			print self.remote_writable_path

	def OnUpdateFiles(self,flist):
		self.updateFlist = flist
		self.OnNextUpdateFiles()

	def OnNextUpdateFiles(self):
		if len(self.updateFlist) > 0 :
			v = self.updateFlist[0]
			fullpath = self.BUILDPATH + v
			relative = os.path.dirname(v)
			filename = os.path.basename(v)

			self.sendFile(fullpath,relative,filename)

			if len(self.updateFlist) > 1:
				self.updateFlist = self.updateFlist[1:]
			else:
				self.updateFlist = []

			QTimer.singleShot(1,self.OnNextUpdateFiles)

		else:
			FILES = ScriptGraphicsProtocol().lua.globals().FILES
			slashProjPath = self.PROJPATH.replace("\\","/")
			slashPlayScene = self.playScene.replace("\\","/")
			playScene = slashPlayScene.replace(slashProjPath+"/","")
			byte = QByteArray()
			line = self.startLine
			if line == None:
				line = 0
			print "line=",line
			startLine = QByteArray.number(line)
			startLine.resize(4)
			byte.append(startLine)
			byte.append(QByteArray(FILES[playScene]))
			self.send("ufin", byte )

	def run(self):
		self.status = 1
		self.send("PATH",QByteArray("AA"))

	def ClearRemoteDist(self):
		shutil.rmtree(self.remote_writable_path)
		os.makedirs(self.remote_writable_path)

	def SendFileList(self):
		self.PROJPATH = ProjectController().path
		self.IMGPATH  = self.PROJPATH + "/image/"
		self.SCENEPATH = self.PROJPATH + "/scene/"
		self.BUILDPATH = self.PROJPATH + "/build/"

		fileList = {}
		for base, dirs, names in os.walk(self.BUILDPATH):
			for name in names :
				fullpath = os.path.join(base, name)
				relative = base.replace(self.BUILDPATH,"")
				extension= os.path.splitext(name)
				
				ID = relative+"/"+extension[0]+extension[1]
				if ID == "/o" or extension[1] == ".obj" :
					continue
					
				ID = ID[1:] if ID.startswith("/") else ID
				fileList[ID] = self.checksum(fullpath)

		checksums = json.dumps(fileList)

		self.send("flst",QByteArray(checksums))

	def __del__(self):
		print "Socket Delete"

	def onDisconnect(self):
		RemoteClient._disconnect_()

	def onRead(self):
		fin = QDataStream(self)
		print "<<<<<<Recived"
		if self.order == None:
			if self.bytesAvailable() >= 4 : 
				self.order = str(fin.device().read(4))
				self.payloadSize = -1
				print "ordered << ",self.order

		print "____0"
		if self.payloadSize == -1 and len(self.order) == 4 : 
			if self.bytesAvailable() >= 11 : 
				self.payloadSize = int(fin.device().read(11))
				self.payload = ""
				print "size << ",self.payloadSize
		
		print "____1"
		if self.order != None and self.payloadSize != -1 : 
			availBytes = self.bytesAvailable()

			print "____2",availBytes,self.payloadSize

			if availBytes > 0 and availBytes < self.payloadSize :
				self.payload += fin.device().read(availBytes)
				self.payloadSize -= availBytes
				availBytes = self.bytesAvailable()

			if availBytes >= self.payloadSize : 
				print "____3"
				self.payload += fin.device().read(self.payloadSize)
				self.payloadSize = 0
				print "____4"

		print "____5"
		if self.order != None and self.payloadSize == 0 and self.payload != None : 
			print "____6"
			self.OnRecved(self.order,self.payloadSize,self.payload)
			print "____7"
			self.order = None
			self.payloadSize = None
			self.payload = None

	def send(self,order,payload):
		if self.live : 
			header=QByteArray(order)
			header.resize(4)

			s_size = str(payload.size())
			size=QByteArray(s_size+" "*(11-len(s_size)))

			#print ">>>>>>>>>>>>>>>>>>>>>>>"
			print "\"",header,"\"",self.write(header)
			print "\"",size,"\"",self.write(size)
			print "payload",self.write(payload)

			OutputWindow().notice(u"리모트 데이터 전송:"+order+" ["+str(payload.size())+"]")

	def sendFile(self,fpath,dist,fname):
		if self.live : 
			fp = QFile( fpath )
			fp.open( QFile.ReadOnly )
			fbyte = fp.readAll()
			fp.close()

			byte = QByteArray()

			dist = dist.replace("\\","/")

			s1 = QByteArray.number(len(dist))
			s1.resize(4)

			dist = QByteArray(dist)
			
			s2 = QByteArray.number(len(fname))
			s2.resize(4)
			
			fname = QByteArray(fname)

			byte.append(s1)
			byte.append(dist)
			byte.append(s2)
			byte.append(fname)
			byte.append(fbyte)

			self.send("tran",byte)
			OutputWindow().notice(u"파일 전송:"+fpath)

	@staticmethod
	def _disconnect_():
		if RemoteClient._instance:
			RemoteClient._instance.status = 0
			RemoteClient._instance.live = False
			RemoteClient._instance.close()

			RemoteClient._isInit = False
			RemoteClient._instance = None
