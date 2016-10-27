# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from PySide.QtGui import *
from PySide.QtCore import *
from PySide.QtNetwork import *
from Noriter.UI.ModalWindow import ModalWindow 
from Noriter.UI.Window import Window 
from Noriter.UI.ListBox import ListBox 
from Noriter.utils.Settings import Settings
from Noriter.views.NoriterMainWindow import *

from controller.ProjectController import ProjectController
from view.OutputWindow import OutputWindow 
from command.RemoteClient import RemoteClient

import socket
import thread, time

class DeviceList(ListBox):
	def __init__(self,factory,parent):
		super(DeviceList,self).__init__(factory,[],False,parent)

	def paintEvent(self,e):
		super(DeviceList,self).paintEvent(e)
		
class ManualWindow(ModalWindow):
	def __init__(self,title="",source="",parent=None):
		super(ManualWindow,self).__init__(parent)

	@LayoutGUI
	def GUI(self):
		self.Layout.label(u"아이피 입력")
		self.Layout.hline();
		self.Layout.gap(3)

		with Layout.HBox():
			self.ip1 = self.Layout.input("192",self.input_ip1)
			self.ip2 = self.Layout.input("168",self.input_ip2)
			self.ip3 = self.Layout.input("0",self.input_ip3)
			self.ip4 = self.Layout.input("",self.input_ip4)

		self.Layout.gap(2)
		self.Layout.hline()
		self.Layout.gap(2)

		self.connect = self.Layout.button(u"연결하기",self.save)
		self.resize(150,0)
		self.ip4.setFocus()

	def input_ip1(self):
		if len(self.ip1.text()) >= 3 : 
			self.ip1.setText(self.ip1.text()[0:3])
			self.ip2.setFocus()

	def input_ip2(self):
		if len(self.ip2.text()) >= 3 : 
			self.ip2.setText(self.ip2.text()[0:3])
			self.ip3.setFocus()

	def input_ip3(self):
		if len(self.ip3.text()) >= 3 : 
			self.ip3.setText(self.ip3.text()[0:3])
			self.ip4.setFocus()

	def input_ip4(self):
		if len(self.ip4.text()) >= 3 : 
			self.ip4.setText(self.ip4.text()[0:3])
			self.connect.setFocus()

	def save(self):
		ip = self.ip1.text() + "." + self.ip2.text() + "." + self.ip3.text() + "." + self.ip4.text()
		
		remote = RemoteClient(NoriterMain())
		remote._connect(ip,45674,False,1)
		remote.playScene = u"scene/메인.lnx";

		self.close()

	def exec_(self):
		super(ManualWindow,self).exec_()

class RemotePlayWindow(ModalWindow):
	def sizeHint(self):
		return QSize(400,140)

	def __init__(self,parent):
		super(RemotePlayWindow,self).__init__(parent)
		self.deviceList.doubleClicked.connect(self.selectDevice)


	def showEvent(self,e):
		super(RemotePlayWindow,self).showEvent(e)
		
		self.udp = QUdpSocket(self)
		self.udp.bind(45675)
		self.udp.readyRead.connect(self.readyRead)

		self.devices = {}

		self.connectionTimer = QTimer(self)
		self.connectionTimer.timeout.connect(self.updateConnection)
		self.connectionTimer.start(1000)

	def hideEvent(self,e):
		super(RemotePlayWindow,self).hideEvent(e)
		self.udp.close()
		self.udp = None

		self.connectionTimer.stop()
		self.connectionTimer = None

	def updateConnection(self):
		destroys = []
		for k,v in self.devices.iteritems(): 
			v[1] -= 1 
			if v[1] <= 0:
				destroys.append(k)

		for v in destroys : 
			del self.devices[v]

		if len(destroys) > 0 :
			self.updateDevice()

	@LayoutGUI
	def GUI(self):
		proCtrl = ProjectController()
		self.deviceList = self.Layout.addWidget(DeviceList(self.factory,self))
		self.Layout.button(self.trUtf8("수동 연결"),self.openIP)

	def readyRead(self):
		buf,addr,port = self.udp.readDatagram(3);
		buf = str(buf)

		if not self.isVisible() : 
			return ;

		ip = addr.toString()

		if not ip in self.devices : 
			self.devices[ip] = [buf,0]
			self.updateDevice()

		self.devices[ip][1] = 3
			
	def updateDevice(self):
		self.deviceList.data = [[k,k,v[0]] for k,v in self.devices.iteritems()]

	def factory(self,v):
		self.Layout.gap(5)
		if v[2] == "WIN" : 
			i = self.Layout.img("resource/device/window.png")
		elif v[2] == "MAC" : 
			i = self.Layout.img("resource/device/osx.png")
		elif v[2] == "AND" : 
			i = self.Layout.img("resource/device/android.png")
		elif v[2] == "IPH" : 
			i = self.Layout.img("resource/device/iphone.png")
		elif v[2] == "IPA" :
			i = self.Layout.img("resource/device/ipad.png")
		else : 
			i = self.Layout.img("resource/device/ipad.png")

		i.setAlignment(Qt.AlignCenter);
		i.setPixmap(i.pixmap().scaled(70,70,Qt.KeepAspectRatio))
		
		i = self.Layout.label(v[1])
		i.setAlignment(Qt.AlignCenter)
		i.setFixedHeight(20)
		return 85

	def selectDevice(self,idx):
		v = self.deviceList.data[idx]

		remote = RemoteClient(NoriterMain())
		remote._connect(v[0],45674,False)
		remote.playScene = u"scene/메인.lnx";

		self.close()

	def openIP(self):
		ManualWindow().exec_()

	def exec_(self):
		super(RemotePlayWindow,self).exec_()
		try:
			pass
		except Exception, e:
			pass
