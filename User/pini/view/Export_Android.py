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

from view.ProgressIndicator import QProgressIndicator

from controller.ProjectController import ProjectController
from controller.SceneListController import SceneListController

import xml.etree.ElementTree as ET

import re
import subprocess
import os
import urllib2
import shutil
import zipfile
import locale
import time
import base64
import hashlib
from PIL import Image
import os_encoding

if sys.platform == "darwin" : 
	pass
else:
	from _winreg import *

PINI_AUTO_ADT_DIST = os.path.expanduser('~')
LUAJIT_PATH = "resource\\tools\\lua\\luajit.exe"

def PJOIN(*paths):
	path = []
	for v in paths:
		v = v.replace("/","\\")
		path.append(v.encode(locale.getpreferredencoding()))
	ret = os.path.join(*path).replace("/","\\")
	return ret

def PROCESS(_arg,**sub):
	sub["stdout"] = subprocess.PIPE
	sub["stdin"] = subprocess.PIPE
	sub["shell"] = True
	fse = sys.getfilesystemencoding()
	_arg = [arg.encode(fse) if isinstance(arg,unicode) else arg for arg in _arg]
	proc = subprocess.Popen(_arg, **sub )
	try:
		out, err = proc.communicate()
		return out
	except Exception, e:
		sys.stderr.write("!!\n")
		return None

def compile_cocos_lua(path,dist):
	luaf = path.replace("/","\\").encode(os_encoding.cp())
	luacf= (dist+"c").replace("/","\\").encode(os_encoding.cp())

	ARGU = [LUAJIT_PATH,"-b",luaf,luacf]
	proc = subprocess.Popen(ARGU, stdout=subprocess.PIPE, stdin=subprocess.PIPE,shell=True )
	try:
		out, err = proc.communicate()
		print ">>>",out,err
	except Exception, e:
		print e

class FileDownload(QObject):
	def __init__(self,parent = None):
		super(FileDownload,self).__init__(parent)
		self.timer = None

	def start(self,url,path,callback):
		if self.timer : 
			return 

		opener = urllib2.build_opener()
		opener.addheaders.append(('Cookie', 'oraclelicense=accept-securebackup-cookie'))
		self.u = opener.open(url)

		self.f = open(path, 'wb')
		self.file_size = int(self.u.info().getheaders("Content-Length")[0])
		
		#print "Downloading: %s Bytes: %s" % (path, self.file_size)

		self.file_size_dl = 0
		self.block_sz = 8192

		def fin():
			self.u.close()
			self.f.close()
			self.timer.stop()
			self.timer = None
			callback(0,0,100,True)

		def work():
			buffer = self.u.read(self.block_sz)
			if not buffer:
				fin()
				return 

			self.file_size_dl += len(buffer)
			self.f.write(buffer)

			callback(self.file_size_dl,self.file_size,self.file_size_dl*100./self.file_size,False)

		self.timer = QTimer()
		self.timer.timeout.connect(work)
		self.timer.start(10)

	def stop(self):
		if self.timer : 
			self.timer.stop()
			self.u.close()
			self.f.close()
			self.timer = None

class Thread_Command(QThread):
	def __init__(self, command, parent = None ):
		super(Thread_Command,self).__init__(parent)
		self.command = command

	def run(self):
		os.system(self.command)
	
class ExportAndroidPermissionWindow(ModalWindow):
	def sizeHint(self):
		return QSize(300,0)

	def __init__(self,parent):
		self.parent = parent
		self.permissionBoxes = {}
		super(ExportAndroidPermissionWindow,self).__init__(parent)

		self._layout.setContentsMargins(5, 5, 5, 5)
		self._layout.setSpacing(4)

		self.modify = False

	def Modified(self):
		self.modify = True
		self.close()

	def exec_(self):
		super(ExportAndroidPermissionWindow,self).exec_()
		try:
			if self.modify : 
				inst = ProjectController()
				with Settings("APK_EXPORT") :
					with Settings(inst.path) :
						for p in self.parent.permissionList:
							Settings()[p] = "1" if self.permissionBoxes[p].isChecked() else "0"
		except Exception, e:
			pass

	@LayoutGUI
	def GUI(self):
		permissions = {}
		for p in self.parent.permissionList:
			permissions[p] = True

		inst = ProjectController()
		with Settings("APK_EXPORT") :
			with Settings(inst.path) :
				for p in self.parent.permissionList:
					permissions[p] = (Settings()[p] == "1") if Settings()[p] else permissions[p]

		self.Layout.label(u"<b>권한 설정</b>")
		self.Layout.hline();
		self.Layout.gap(3)

		with Layout.VBox(5):
			for p in self.parent.permissionList:
				self.permissionBoxes[p] = self.Layout.checkbox(unicode(p), permissions[p], None)

		with Layout.HBox(5):
			self.Layout.button(self.trUtf8("수정"),self.Modified)
			self.Layout.button(self.trUtf8("취소"),self.close)


class ExportAndroidWindow(ModalWindow):
	def sizeHint(self):
		return QSize(300,0)

	def __init__(self,src=None,parent=None):
		self.work_step = 0

		super(ExportAndroidWindow,self).__init__(parent)
		self.setWindowTitle(u"안드로이드 익스포트")
		self.nextStep()

		self.inJdkPath = ""
		self.inAdtPath = ""

		self.download = None
		self.installThread = None
		self.indicator = None
		self.reserveTestRun = False

		self.permissionList = []
		self.permissionList.append("android.permission.INTERNET")
		self.permissionList.append("android.permission.CHANGE_NETWORK_STATE")
		self.permissionList.append("android.permission.CHANGE_WIFI_STATE")
		self.permissionList.append("android.permission.ACCESS_NETWORK_STATE")
		self.permissionList.append("android.permission.ACCESS_WIFI_STATE")
		self.permissionList.append("android.permission.VIBRATE")
		self.permissionList.append("com.android.vending.BILLING")
		self.permissionList.append("android.permission.MOUNT_UNMOUNT_FILESYSTEMS")
		self.permissionList.append("android.permission.WRITE_EXTERNAL_STORAGE")
		self.permissionList.append("android.permission.WAKE_LOCK")
		self.permissionList.append("com.android.vending.CHECK_LICENSE")

	def resizeEvent(self,e):
		if e :
			super(ExportAndroidWindow,self).resizeEvent(e)
		if self.indicator : 
			p = self.indicator.parent()
			self.indicator.move(p.width()/2-10,p.height()/2-10)

	def closeEvent(self,e):
		super(ExportAndroidWindow,self).closeEvent(e)
		if self.download : 
			self.download.stop()
			self.download = None

		if self.installThread : 
			self.installThread.terminate()
			self.installThread = None

	def doReserveTestRun(self):
		self.reserveTestRun = True
		self.nextStep()

	def nextStep(self):
		if self.work_step == 0 : 
			self.work_step = 1
		elif self.work_step == 1 : 
			self.inJdkPath = self.inJ.text();
			self.inAdtPath = self.inA.text();
			self.work_step = 2
		elif self.work_step == 2 : 
			self.work_step = 3
		elif self.work_step == 3 : 
			if os.path.isdir(self.savePath.text()) == False :
				QMessageBox.warning(self,"Pini",u"선택한 저장 위치가 존재하지 않거나 폴더가 아닙니다.")
				return 
			if len(self.saveGameName.text()) <= 0 : 
				QMessageBox.warning(self,"Pini",u"게임명을 반드시 기제해주셔야합니다.")
				return 
			if len(self.savePackageName.text()) <= 0 : 
				QMessageBox.warning(self,"Pini",u"패키지명을 반드시 기제해주셔야합니다.")
				return 
			if self.savePackageName.text().find(" ") >= 0 : 
				QMessageBox.warning(self,"Pini",u"패키지명에 공백이 들어갈 수 없습니다.")
				return 
			if len(self.savePassword.text()) < 8 : 
				QMessageBox.warning(self,"Pini",u"패스워드는 8자 이상이여야합니다.")
				return 
			match = re.match("[a-zA-Z0-9]*",self.savePassword.text())
			if match == None or len(match.group()) != len(self.savePassword.text()) : 
				QMessageBox.warning(self,"Pini",u"패스워드는 영어 혹은 숫자로만 입력되야합니다.")
				return 

			match = re.match(r"[0-9\.]+",self.saveVersion.text())
			if match == None or len(self.saveVersion.text()) != len(match.group()) : 
				QMessageBox.warning(self,"Pini",u"버전은 숫자와 .으로만 구성되어야합니다.")
				return

			self.work_step = 4

		self.GUI()

		if self.work_step == 2 : 
			self.nextbtn.setEnabled(False)
			self.check_dev_dep()
		elif self.work_step == 4 : 
			self.nextbtn.setEnabled(False)

			self.savePackageName = self.savePackageName.text()
			self.saveGameName = self.saveGameName.text()
			self.savePassword = self.savePassword.text()
			self.saveVersion = self.saveVersion.text()
			self.savePath = self.savePath.text()
			self.isEncryptionEnable = self.isEncryptionEnable.currentIndex()

			QTimer.singleShot(1, self.export_apk )

	def export_apk(self):
		#create keystore
		package = self.savePackageName
		game = self.saveGameName
		password = self.savePassword
		apkpath = self.savePath
		version = self.saveVersion
		iconpath = "resource/export_default_icon.png"
		isEncryptionEnable = self.isEncryptionEnable

		inst = ProjectController()
		with Settings("APK_EXPORT") :
			with Settings(inst.path) :
				if Settings()["iconpath"] : 
					iconpath = Settings()["iconpath"]  
			
				Settings()["path"]     = apkpath
				Settings()["package"]  = package
				Settings()["game"]     = game
				Settings()["version"]  = version
				Settings()["password"] = password
				Settings()["__encryptionEnable"] = isEncryptionEnable + 1

		def step1():
			self.progressText.setText(u"키스토어 생성")

			PROJPATH = inst.path
			projKeystorePath = PJOIN(PROJPATH,"keystore")
			projKeystore = PJOIN(PROJPATH,"keystore",".keystore")
			if os.path.isdir(projKeystorePath) == False :
				os.mkdir(projKeystorePath)

				if os.path.isdir("keystore") == True : 
					keystorePath = PJOIN("keystore",package)
					keystore = PJOIN(keystorePath,".keystore")

					if os.path.isdir(keystorePath) == True:
						# 기존 폴더에 존재하므로, 현재 폴더로 복사해옵니다.
						print "copy keystore"
						shutil.copyfile(keystore,projKeystore)
						return

				# 키스토어가 없으므로, 생성합니다
				print "make keystore"

				QMessageBox.warning(self,"Pini",u"키스토어를 생성합니다.\n"
						+"키스토어는 구글 플레이스토어 마켓 등록 및 관리에 필수적인 파일이며, 분실할시 업데이트를 진행할 수 없게 됩니다.\n"
						+"프로젝트 폴더의 keystore 폴더의 .keystore 파일로 저장되며, 백업을 권장드립니다!")

				name = "dev"
				team = "team"
				company = "company"

				KEYTOOL = PJOIN(Settings()["JDK_PATH"],"bin","keytool")
				_arg = [
					KEYTOOL,
					"-genkey","-v",
					"-keystore",projKeystore,
					"-alias",package,
					"-keyalg","RSA","-keysize","2048","-validity","10000",
					"-keypass",password,"-storepass",password,
					"-dname","cn="+name+", ou="+team+", o="+company+", c=KR"
				]

				print PROCESS(_arg)

		def step2():
			self.progressText.setText(u"임시 파일 삭제")
			try:
				shutil.rmtree("./resource/android/tmp")
			except Exception, e:
				print e

		def step3(): 
			### decompile!
			self.progressText.setText(u"APK 수정 중")
			#if os.path.isdir("./android/tmp/") :
			#	os.makedirs("./android/tmp/")
			JAVABIN = PJOIN(Settings()["JDK_PATH"],"bin","java")
			currentCwd=os.getcwd().decode('mbcs')
			APKTOOL = PJOIN(currentCwd,"resource","tools","win32","apktool","apktool.jar")
			TMPPATH = PJOIN(currentCwd,"resource","android","tmp")
			APKPATH1 = PJOIN(currentCwd,"resource","android","PiniRemote-portrait.apk")
			APKPATH2 = PJOIN(currentCwd,"resource","android","PiniRemote-landscape.apk")
			if inst.orientation :
				_arg = [JAVABIN,
						"-jar", APKTOOL,
						"d","-o",
						TMPPATH,
						APKPATH1
				]
				PROCESS(_arg)
			else:
				_arg = [JAVABIN,
						"-jar",APKTOOL,
						"d","-o",
						TMPPATH,
						APKPATH2
				]
				PROCESS(_arg)
		
		def step4():
			### replace xml 
			try:
				self.progressText.setText(u"XML 수정")
				doc = ET.parse("./resource/android/tmp/AndroidManifest.xml")
				ET.register_namespace('android', 'http://schemas.android.com/apk/res/android')
				root = doc.getroot()
				root.attrib["package"] = package
				root.attrib["{http://schemas.android.com/apk/res/android}versionCode"] = str(int(version.replace(".","")))
				root.attrib["{http://schemas.android.com/apk/res/android}versionName"] = version
				
				permissions = [permission for permission in root.iter("uses-permission")]

				toRemove = []

				inst = ProjectController()
				with Settings("APK_EXPORT") :
					with Settings(inst.path) :
						for p in self.permissionList:
							currentPermission = (Settings()[p] == "1") if Settings()[p] else True

							if not currentPermission:
								toRemove.append(p)

				for permission in permissions:
					if permission.attrib["{http://schemas.android.com/apk/res/android}name"] in toRemove:
						root.remove(permission)

				doc.write("./resource/android/tmp/AndroidManifest.xml", encoding="utf-8", xml_declaration=True)

				### replace strings xml 
				doc = ET.parse("./resource/android/tmp/res/values/strings.xml")
				root = doc.getroot()
				for child in root:
					if child == None : 
						break;
					if child.attrib["name"] == "app_name" : 
						child.text = game
						break;
				doc.write("./resource/android/tmp/res/values/strings.xml", encoding="utf-8", xml_declaration=True)
			
			except Exception, e:
				print e
				QMessageBox.warning(self,"Pini",u"XML 수정에 실패하였습니다.\n"+str(e))
				return False

		def step5():
			self.progressText.setText(u"리소스 변경")
			### resource move!

			try:
				DISTPATH = "./resource/android/tmp/assets/src/"
				f = open(DISTPATH+'_export_execute_.lua', 'w')
				f.write("return '' ")
				f.close();

				inst = ProjectController()
				inst.compileProj()

				PROJPATH = inst.path
				BUILDPATH = PROJPATH + "/build/"
				BUILDPATH = BUILDPATH.replace("\\","/")

				#print BUILDPATH,dist
				#shutil.copytree(BUILDPATH,dist)
				for root, dirs, files in os.walk(BUILDPATH, topdown=False):
					for name in files:
						path = os.path.join(root, name).replace("\\","/")
						ext  = os.path.splitext(path)[1]
						dist = os.path.join(DISTPATH,path.replace(BUILDPATH,"")).replace("\\","/")

						if ext==".obj" : 
							continue

						if os.path.isdir(os.path.dirname(dist)) == False :
							os.makedirs(os.path.dirname(dist))

						if ext==".lua" : 
							compile_cocos_lua(path,dist)
						else:
							fr = open(path, 'rb')
							fs = open(dist, 'wb')

							fs.write(fr.read())

							fr.close()
							fs.close()

				if os.path.isdir(DISTPATH+"/etc") : 
					if os.path.isdir(DISTPATH+"/../etc") : 
						shutil.rmtree(DISTPATH+"/../etc")
					shutil.move(DISTPATH+"/etc", DISTPATH+"/../etc")

				RES_DIST = "./resource/android/tmp/res/"
				img = Image.open(iconpath)
				img.resize((144,144), Image.ANTIALIAS).save(RES_DIST+"drawable-xxhdpi/icon.png")
				img.resize((96,96), Image.ANTIALIAS).save(RES_DIST+"drawable-xhdpi/icon.png")
				img.resize((72,72), Image.ANTIALIAS).save(RES_DIST+"drawable-hdpi/icon.png")
				img.resize((48,48), Image.ANTIALIAS).save(RES_DIST+"drawable-mdpi/icon.png")
				img.resize((32,32), Image.ANTIALIAS).save(RES_DIST+"drawable-ldpi/icon.png")

			except Exception, e:
				print e
				QMessageBox.warning(self,"Pini",u"리소스 변경에 실패하였습니다.\n"+str(e))
				return False

			if self.isEncryptionEnable == 1:
				self.progressText.setText(u"암호화 중")
				print "ENCRYPT START"
				# 이미지와 사운드 폴더만 압축합니다
				# 리소스는 2GB 를 넘지 않는다고 가정합니다.
				try:
					SEVENZIPPATH = "resource\\tools\\win32\\7z\\7z.exe"
					base_password = str(time.time())
					print "base_password=",base_password
					base_password = base64.b64encode(hashlib.md5(base_password).digest())
					print "after md5:",base_password

					with open(DISTPATH+'pp.lua', 'w') as f:
						f.write("return function() return \"" + base_password + "\" end" )

					with open(DISTPATH+'../pp.lua', 'w') as f:
						f.write("return function() return \"" + base_password + "\" end" )

					base_password = base_password[0:11]

					isImageExist = os.path.exists(DISTPATH+"image")
					isSoundExist = os.path.exists(DISTPATH+"sound")

					targetFolders = []

					if isImageExist:
						targetFolders.append(DISTPATH+'image')
					if isSoundExist:
						targetFolders.append(DISTPATH+'sound')

					rc = subprocess.call([SEVENZIPPATH,'a','-tzip','-p'+base_password,'-r','-y',DISTPATH+'/../res.prz'] + targetFolders)

					if isImageExist:
						shutil.rmtree(DISTPATH+"image")
					if isSoundExist:
						shutil.rmtree(DISTPATH+"sound")

				except Exception, e:
					print e
					QMessageBox.warning(self,"Pini",u"암호화에 실패하였습니다.\n")
					return False
				print "ENCRYPT END"
			elif self.isEncryptionEnable == 2:
				self.progressText.setText(u"확장파일 생성 중")
				print "EXTENSION START"
				# 이미지와 사운드 폴더만 압축합니다
				# 리소스는 2GB 를 넘지 않는다고 가정합니다.
				try:
					SEVENZIPPATH = "resource\\tools\\win32\\7z\\7z.exe"
					
					base_password = str(time.time())
					print "base_password=",base_password
					base_password = base64.b64encode(hashlib.md5(base_password).digest())
					print "after md5:",base_password

					f = open(DISTPATH+'pp.lua', 'w')
					f.write("return function() return \"" + base_password + "\" end" )
					f.close();

					base_password = base_password[0:11]

					isImageExist = os.path.exists(DISTPATH+"image")
					isSoundExist = os.path.exists(DISTPATH+"sound")

					targetFolders = []

					if isImageExist:
						targetFolders.append(DISTPATH+'image')
					if isSoundExist:
						targetFolders.append(DISTPATH+'sound')

					rc = subprocess.call([SEVENZIPPATH,'a','-tzip','-p'+base_password,'-r','-y',(apkpath.encode(locale.getpreferredencoding()))+'/extension.prz'] + targetFolders)

					if isImageExist:
						shutil.rmtree(DISTPATH+"image")
					if isSoundExist:
						shutil.rmtree(DISTPATH+"sound")

				except Exception, e:
					print e
					QMessageBox.warning(self,"Pini",u"확장파일 생성에 실패하였습니다.\n")
					return False
				print "EXTENSION END"

		def step6():
			self.progressText.setText(u"컴파일 중")

			try:
				os.makedirs(apkpath.encode(locale.getpreferredencoding()))
			except Exception, e:
				pass

			path = PJOIN(apkpath,u"android_publish.apk")

			cwd=os.getcwd().decode('mbcs')
			JAVABIN = PJOIN(Settings()["JDK_PATH"],"bin","java")
			APKTOOL = PJOIN(cwd,"resource","tools","win32","apktool","apktool.jar")
			TMPPATH = PJOIN(cwd,"resource","android","tmp")
			
			_arg = [JAVABIN,
					"-jar", APKTOOL,
					"b","-o",
					path,
					TMPPATH
			]
			
			os.chdir(PJOIN("resource","tools","win32","apktool"))
			PROCESS(_arg)
			os.chdir(PJOIN("..","..","..",".."))

		def step7():
			self.progressText.setText(u"서명 인증 중 ")
			PROJPATH = inst.path
			keystorePath = PJOIN(PROJPATH,"keystore")
			keystore = PJOIN(PROJPATH,"keystore",".keystore")
		
			path1 = PJOIN(apkpath,u"android_publish.apk")
			path2 = PJOIN(apkpath,u"android_publish.signed.apk")
		
			SIGNER = PJOIN(Settings()["JDK_PATH"],"bin","jarsigner")
			
			_arg = [SIGNER,
					"-verbose",
					"-sigalg","SHA1withRSA","-digestalg","SHA1",
					"-keystore", keystore,
					"-keypass",password,
					"-storepass",password,
					path1, package
			]

			out = PROCESS(_arg)

			if out : 
				if out.find("password was incorrect") >= 0 :
					QMessageBox.warning(self,"Pini",u"비밀번호가 틀렸습니다.\n최초 입력한 비밀번호를 다시 입력해주세요.")
					return False
				if out.find("jarsigner: Certificate chain not found for:") >= 0:
					QMessageBox.warning(self,"Pini",u"APK 서명이 실패하였습니다. 패키지명이 키스토어를 만들 때와 다릅니다.");
					return False
				if out.find("jarsigner error: java.lang.RuntimeException: keystore load:") >= 0:
					QMessageBox.warning(self,"Pini",u"APK 서명이 실패하였습니다. keystore 폴더에 .keystore 파일이 존재하지 않습니다.");
					return False

			else:
				return False
		def step8():
			self.progressText.setText(u"임시파일 삭제")
			try:
				shutil.rmtree("resource/android/tmp")
				path1 = PJOIN(apkpath,u"android_publish.apk")
				path2 = PJOIN(apkpath,u"android_publish_ziped.apk")

				ADT = Settings()["ADT_PATH"]
				zipalign_path = None
				for root, dirs, files in os.walk(ADT, topdown=False):
					for name in files:
						if name == "zipalign.exe" : 
							zipalign_path = PJOIN(root, name)
							break

				if zipalign_path == None : 
					QMessageBox.warning(self,"Pini",u"ADT에서 build-tools를 찾지 못했습니다.\nhttp://nooslab.com/piniengine/wiki/index.php?title=Tutorial:export_game 에서 'ADT 수동설치시, 최신버젼으로 업데이트 하기'를 진행해주세요.\n페이지로 이동합니다. ")
					QDesktopServices.openUrl(QUrl("http://nooslab.com/piniengine/wiki/index.php?title=Tutorial:export_game#ADT_MANUAL"))
					return

				_arg = [zipalign_path,
					"-v",
					"4",
					path1, path2
				]

				out = PROCESS(_arg)

				targetFileName = ""
				for c in game:
					if re.match(u"[a-zA-Z0-9ㄱ-ㅎㅏ-ㅣ가-힣]", c):
						targetFileName = targetFileName + c
					else:
						targetFileName = targetFileName + "_"

				if os.path.isfile(path2) : 
					path3 = PJOIN(apkpath,targetFileName+u".apk")
					count = 1
					while 1 :
						try:
							try:
								os.remove(path3)
							except Exception, e:
								pass
							os.rename(path2,path3)
							os.remove(path1)
							break
						except Exception, e:
							if count > 200:
								path3 = path2
								os.remove(path1)
								break
							elif count > 100:
								path3 = PJOIN(apkpath,"pini_export("+str(count-100)+")"+u".apk")
							else:
								path3 = PJOIN(apkpath,targetFileName+"("+str(count)+")"+u".apk")
							count += 1

					if count > 1:
						QMessageBox.warning(self,"Pini",u"지정한 경로에 파일을 저장하지 못하여 '"+path3+u"' 경로에 apk를 저장했습니다.");
				else:
					QMessageBox.warning(self,"Pini",u"APK 서명이 실패하였습니다. 이전에 서명한 keystore파일이 맞는지 확인해주시기바랍니다.");
					return False
			except Exception, e:
				print e
				QMessageBox.warning(self,"Pini",u"알 수 없는 에러가 발생했습니다.\n"+str(e))
				return False

		self.step = 0
		self.steps = [step1,step2,step3,step4,step5,step6,step7,step8]
		def onStep():
			if self.step >= len(self.steps):
				self.progressText.setText(u"APK 생성 완료")

				if self.reserveTestRun:
					self.APKTestRun()
				else:
					self.nextbtn.setEnabled(True)
				return
			if self.steps[self.step]() == False : 
				self.work_step = 0
				self.nextStep()
				return 

			self.progress.setValue( float(self.step+1)/float(len(self.steps)) * 100 )
			self.step+=1
			QTimer.singleShot(1,onStep)
		onStep()

	def check_dev_dep(self):
		self.NeedJDKInstall = True
		self.NeedADTInstall = True

		self.TryADTInstall = False
		self.TryJDKInstall = False

		self.NeedJREInstall = True

		if self.inJdkPath != u"자동 설치":
			if self.checkJDKPath(self.inJdkPath) : 
				self.NeedJDKInstall = False

		if self.inAdtPath != u"자동 설치":
			if self.checkADTPath(self.inAdtPath) : 
				self.NeedADTInstall = False

		self.NeedJREInstall = not self.checkJRESetup()

		def processing():
			if self.NeedJREInstall :
				QMessageBox.warning(self,"Pini",u"JRE 가 설치되어있지 않거나 JRE 1.8버전이 깔려있지 않습니다.\n깔려있는 JRE 을 모두 지우신 뒤, 1.8 버전을 설치하세요.\nJRE다운로드 페이지를 연결합니다.")
				QDesktopServices.openUrl(QUrl("http://www.oracle.com/technetwork/java/javase/downloads/jre8-downloads-2133155.html"))
				self.work_step = 0;
				self.nextStep()
				return

			if self.NeedJDKInstall :
				self.TryJDKInstall = True
				self.NeedJDKInstall= False
				install_JDK();
				return

			if self.TryJDKInstall : 
				if self.FindJDK() == None : 
					QMessageBox.warning(self,"Pini",u"JDK 자동설치에 실패하였습니다.\n직접 JDK를 설치하여 경로를 설정해주세요.\nJDK다운로드 페이지를 연결합니다.")
					QDesktopServices.openUrl(QUrl("http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html"))
					self.work_step = 0;
					self.nextStep()
					return

			if self.NeedADTInstall :
				self.TryADTInstall = True
				self.NeedADTInstall= False
				install_ADT()
				return
				
			if self.TryADTInstall : 
				if self.FindADT() == None  :
					QMessageBox.warning(self,"Pini",u"ADT 자동설치에 실패하였습니다.\n직접 ADT를 설치하여 경로를 설정해주세요.\nADT다운로드 페이지를 연결합니다.")
					QDesktopServices.openUrl(QUrl("http://developer.android.com/sdk/index.html#Other"))
					self.work_step = 0;
					self.nextStep()
					return 

			self.work_step = 2
			self.nextStep()

		def install_ADT():
			def ADT_INSTALL():
				#os.rename( ".\\adt.zip" , PINI_AUTO_ADT_ZIP.replace("/","\\") )

				self.progressText.setText(u"ADT 압축 해제 중. (1-2분의 시간이 소요 됩니다. 잠시만 기다려주세요.)")
				self.progress.setValue(0)

				self.indicator = QProgressIndicator(self.progress)
				self.indicator.setAnimationDelay(70)
				self.indicator.startAnimation()
				#android update sdk -u -a -t 1,2,3
				def ADT_FIN():
					Settings()["ADT_PATH"] = PJOIN(PINI_AUTO_ADT_DIST,"android-sdk-windows")
					self.progressText.setText(u"ADT 설치 완료")
					self.indicator.close()
					self.indicator = None
					if os.path.exists( "./adt.zip" ) :
						os.remove( "./adt.zip" )
					processing();

				def adt_update():
					self.progressText.setText(u"ADT 업데이트 중. (4-5분의 시간이 소요 됩니다. 잠시만 기다려주세요.)")
					def _u():
						proc = subprocess.Popen([ PINI_AUTO_ADT_DIST.replace("/","\\")+"\\android-sdk-windows\\tools\\android.bat", "update", "sdk", "-u", "-a", "-t", "1,2,3"], stdout=subprocess.PIPE, stdin=subprocess.PIPE,shell=True )
						try:
							out, err = proc.communicate("y\n")
							print out, err
						except Exception, e:
							pass

						ADT_FIN();
					QTimer.singleShot(1,_u)

				def extract():
					fzip = zipfile.ZipFile("./adt.zip", 'r')
					fzip.extractall(path=PINI_AUTO_ADT_DIST)
					fzip.close()

					adt_update()
				QTimer.singleShot(1,extract)

			def ADT_DOWNLOAD_PROCESSING(current,total,parentage,fin):
				self.progressText.setText(u"ADT 다운로드 중 ["+str(current)+"/"+str(total)+"]")
				self.progress.setValue(parentage)
				if fin : 
					ADT_INSTALL()

			self.progressText.setText(u"ADT 다운로드 중 []")

			adt_url = "http://dl.google.com/android/android-sdk_r24-windows.zip"
			self.file = FileDownload()
			self.file.start(adt_url,"./adt.zip",ADT_DOWNLOAD_PROCESSING)

		def install_JDK():
			def JDK_INSTALL():
				def JDK_FIN_INSTALL():
					self.progressText.setText(u"JDK 설치 완료")
					self.installThread = None
					self.indicator.close()
					self.indicator = None
					if os.path.exists("./jdk.exe") :
						os.remove("./jdk.exe")
					processing();

				self.progressText.setText(u"JDK 설치 중 (3-4분의 시간이 소요 됩니다. 잠시만 기다려주세요.)")

				self.progress.setValue(0)
				self.indicator = QProgressIndicator(self.progress)
				self.indicator.setAnimationDelay(70)
				self.indicator.startAnimation()

				self.installThread = Thread_Command("start /w .\\jdk.exe /s")
				self.installThread.finished.connect(JDK_FIN_INSTALL)
				self.installThread.start()

				self.resizeEvent(None)

			def JDK_DOWNLOAD_PROCESSING(current,total,parentage,fin):
				self.progressText.setText(u"JDK 다운로드 중 ["+str(current)+"/"+str(total)+"]")
				self.progress.setValue(parentage)
				if fin : 
					JDK_INSTALL()

			self.progressText.setText(u"JDK 다운로드 중 []")

			try:
				jdk_url = "http://download.oracle.com/otn-pub/java/jdk/8u25-b18/jdk-8u25-windows-i586.exe"
				if 'x86' in os.environ['PROGRAMFILES'] : 
					jdk_url = "http://download.oracle.com/otn-pub/java/jdk/8u25-b18/jdk-8u25-windows-x64.exe"
				
				print jdk_url

				self.download = FileDownload()
				self.download.start(jdk_url,"./jdk.exe",JDK_DOWNLOAD_PROCESSING)
			except Exception, e:
				processing()
		processing()

	def checkADTPath(self,path):
		adb = PJOIN(path,"platform-tools","adb.exe")
		try:
			out = PROCESS([adb, "version"])
			if out : 
				return out.startswith("Android Debug Bridge version") if out else False
			else:
				return False
		except Exception, e:
			return False

	def checkJDKPath(self,path):
		signer = PJOIN(path,"bin","jarsigner.exe")
		signer = signer.replace("/","\\") 
		signer = signer.replace("\\\\","\\")
		try:
			out = PROCESS([signer])
			if out : 
				return out.find("jarsigner [options] jar-file alias") if out else False
			else:
				return None
		except Exception, e:
			return None

	def checkJRESetup(self):
		aReg = ConnectRegistry(None,HKEY_LOCAL_MACHINE)
		try:
			aKey = None

			if 'x86' in os.environ['PROGRAMFILES'] : 
				aKey = OpenKey(aReg, r"SOFTWARE\\JavaSoft\\Java Runtime Environment", 0, KEY_READ | KEY_WOW64_64KEY)
			else :
				aKey = OpenKey(aReg, r"SOFTWARE\\JavaSoft\\Java Runtime Environment")

			for i in range(1024):
				try:
					n,v,t = EnumValue(aKey,i)

					if n == "CurrentVersion":
						if v == "1.8":
							return True
				except WindowsError:
					break
			CloseKey(aKey)
		except WindowsError:
			pass
		CloseKey(aReg)
		return False

	def FindADT(self):
		if Settings()["ADT_PATH"] :
			#for window!
			path = Settings()["ADT_PATH"]
			if self.checkADTPath(path) :
				return path
		return None 

	def FindJDK(self):
		print Settings()["JDK_PATH"]
		if Settings()["JDK_PATH"] and len(Settings()["JDK_PATH"]) > 2 :
			#for window!
			path = Settings()["JDK_PATH"]
			if self.checkJDKPath(path) :
				return path
			else : 
				Settings()["JDK_PATH"] = " "
				return self.FindJDK()
		else:
			jdk_default_path = "C:/Program Files/Java"
			if os.path.isdir(jdk_default_path) : 
				for root, dirs, files in os.walk(jdk_default_path, topdown=False):
					for name in files:
						if name == "jarsigner.exe" : 
							path = PJOIN(root, name).replace("\\","/")
							path = path.replace("bin/jarsigner.exe","")
							Settings()["JDK_PATH"] = path
							return path
		return None 

	def btn_find_adt(self):
		path = QtGui.QFileDialog.getExistingDirectory(parent=self,caption="Select ADT" )
		if path : 
			#for window!
			if self.checkADTPath(path) :
				self.inA.setText(path)
				QMessageBox.information(self,"Pini",u"'안드로이드 개발자 툴'(ADT)을 정상적으로 검색하였습니다.")
				Settings()["ADT_PATH"] = path
			else:
				QMessageBox.warning(self,"Pini",u"선택한 경로에는 '안드로이드 개발자 툴'(ADT)가 없습니다.")

	def btn_find_jdk(self):
		path = QtGui.QFileDialog.getExistingDirectory(parent=self,caption="Select JDK" )
		if path : 
			#for window!
			if self.checkJDKPath(path) :
				self.inJ.setText(path)
				QMessageBox.information(self,"Pini",u"'자바 개발자 킷'(JDK)을 정상적으로 검색하였습니다.")
				Settings()["JDK_PATH"] = path
			else:
				QMessageBox.warning(self,"Pini",u"선택한 경로에는 '자바 개발자 킷'(JDK)가 없습니다.")

	def btn_find_save_apk(self):
		path = QtGui.QFileDialog.getExistingDirectory(parent=self,caption="Select APK Save Directory" )
		if path : 
			inst = ProjectController()
			with Settings("APK_EXPORT") :
				with Settings(inst.path) :
					Settings()["path"] = path
			self.savePath.setText(path)

	def btn_change_permission(self):
		ExportAndroidPermissionWindow(self).exec_()

	def find_icon(self):
		path,ext = QFileDialog.getOpenFileName(parent=self,caption=u"아이콘으로 사용할 이미지를 선택해주세요.",filter="JPEG (*.jpg *.jpeg);;PNG (*.png);;" )
		if path : 
			inst = ProjectController()
			with Settings("APK_EXPORT") :
				with Settings(inst.path) :
					Settings()["iconpath"] = path
					self.appIcon.setPixmap(path)

	def APKTestRun(self):
		self.work_step = -1
		self.GUI()

	def startTestRun(self):
		self.resize(300,300)
		def LOG(text):
			self.log.setText(self.log.toPlainText()+text+"\n");

		def CMD(*args):
			_args = list(args)
			out = PROCESS(_args)
			if out : 
				LOG(out)
			
		package = self.savePackageName
		game = self.saveGameName
		apkpath = self.savePath
		apkpath = PJOIN(apkpath,game) + ".apk"

		ADT_PATH = self.FindADT()
		ADBPATH = PJOIN(ADT_PATH,"platform-tools","adb.exe")

		def step1():
			LOG(u"기기 연결 대기")
			LOG(u"설치된 앱 삭제")
			CMD(ADBPATH,"uninstall",package)
			#print os.system("adb uninstall com.nooslab.piniengine")

		def step2():
			print apkpath
			LOG(u"기기 연결 대기")
			LOG(u"앱 설치")
			CMD(ADBPATH,"install",apkpath)
			#print os.system("adb install "+newapk)
			
		def step3():
			LOG(u"기기 연결 대기")
			LOG(u"앱 실행")
			CMD(ADBPATH,"shell","am","start","-a","android.intent.action.MAIN","-n",package+"/org.cocos2dx.lua.AppActivity")
			#print os.system("adb shell am start -a android.intent.action.MAIN -n com.nooslab.piniengine/org.cocos2dx.lua.AppActivity")
		
		self.step = 0
		self.steps = [step1,step2,step3]
		def onStep():
			if self.step >= len(self.steps):
				return
			self.steps[self.step]()
			self.step+=1
			QTimer.singleShot(1000,onStep)
		onStep()


	@LayoutGUI
	def GUI(self):
		self.Layout.clear()
		if self.work_step == 1 : 
			self.step1_GUI()
		elif self.work_step == 2:
			self.step2_GUI()
		elif self.work_step == 3:
			self.step3_GUI()
		elif self.work_step == 4:
			self.step4_GUI()
		elif self.work_step == -1: 
			self.testRun_GUI()
		self.resize(300,0)
		if self.work_step == 3 : 
			self.resize(360,0)

	def step1_GUI(self):
		self.Layout.label("<b>1. 안드로이드 개발자 세팅 체크</b>")
		self.Layout.hline();
		self.Layout.gap(3)

		path = self.FindADT()
		path = path if path else u"자동 설치"

		with Layout.HBox():
			self.Layout.label(u"ADT 위치")
			self.inA = self.Layout.input(path,None)
			self.Layout.button(u"...",self.btn_find_adt).setFixedHeight(20)

			self.inA.setReadOnly(True)
		
		path = self.FindJDK()
		path = path if path else u"자동 설치"
		
		self.Layout.gap(3)
		with Layout.HBox():
			self.Layout.label(u"JDK 위치")
			self.inJ = self.Layout.input(path,None)
			self.Layout.button(u"...",self.btn_find_jdk).setFixedHeight(20)

			self.inJ.setReadOnly(True)

		self.Layout.gap(3)
		self.nextbtn = self.Layout.button(u"다음",self.nextStep)#.setFixedHeight(20);

	def step2_GUI(self):
		self.Layout.label(u"<b>2. 개발툴 다운로드</b>")
		self.Layout.hline();
		self.Layout.gap(3)

		self.progressText = self.Layout.label(u"설치 설명.")
		self.progress = self.Layout.addWidget(QProgressBar(self))
		self.nextbtn = self.Layout.button(u"다음",self.nextStep)#.setFixedHeight(20);

		self.progress.setMaximum(100)
		self.progress.setMinimum(0)
		self.progress.setValue(0)

	def step3_GUI(self):
		inst = ProjectController()

		savepath = os.path.expanduser('~') + '/Desktop/'
		savepath = savepath.replace("/","\\")
		gamename = "game"
		packagename = "com.team.game"
		version = "0.1"
		password = ""
		iconpath = "resource/export_default_icon.png"
		encryptionEnable = False

		with Settings("APK_EXPORT") :
			with Settings(inst.path) :
				savepath = Settings()["path"] if Settings()["path"] else savepath
				gamename = Settings()["game"] if Settings()["game"] else gamename
				packagename = Settings()["package"] if Settings()["package"] else packagename
				version = Settings()["version"] if Settings()["version"] else version
				password = Settings()["password"] if Settings()["password"] else password
				iconpath = Settings()["iconpath"] if Settings()["iconpath"] else iconpath
				encryptionEnable = Settings()["__encryptionEnable"]
				if encryptionEnable : 
					encryptionEnable = encryptionEnable-1

		self.Layout.label(u"<b>3. apk 정보 설정</b>")
		self.Layout.hline();
		self.Layout.gap(3)
		
		with Layout.HBox():
			with Layout.VBox():
				with Layout.HBox():
					self.Layout.label(u"저장위치").setFixedWidth(70)
					self.savePath = self.Layout.input(savepath,None)
					self.Layout.button(u"...",self.btn_find_save_apk).setFixedHeight(20);
				with Layout.HBox():
					self.Layout.label(u"게임명").setFixedWidth(70)
					self.saveGameName = self.Layout.input(gamename,None)
				with Layout.HBox():
					self.Layout.label(u"패키지명").setFixedWidth(70)
					self.savePackageName = self.Layout.input(packagename,None)
				with Layout.HBox():
					self.Layout.label(u"앱 버전").setFixedWidth(70)
					self.saveVersion = self.Layout.input(version,None)
				with Layout.HBox():
					self.Layout.label(u"비밀번호").setFixedWidth(70)
					self.savePassword = self.Layout.input(password,None)
				with Layout.HBox():
					self.Layout.button(u"권한 설정",self.btn_change_permission).setFixedHeight(20);

			self.Layout.gap(5)
			
			with Layout.VBox():
				self.appIcon = self.Layout.img(iconpath)#.setFixedSize(50,50)
				self.appIcon.setFixedSize(90,90)
				self.Layout.button(u"...",self.find_icon).setFixedHeight(20)
				self.isEncryptionEnable = self.Layout.combo([u"빌드옵션없음",u"리소스암호화",u"확장파일사용"])#self.Layout.checkbox(u"리소스 암호화", encryptionEnable, None)
				if encryptionEnable:
					self.isEncryptionEnable.setCurrentIndex(encryptionEnable)
				#self.isEncryptionEnable = self.Layout.checkbox(u"리소스 암호화", encryptionEnable, None)
		#self.Layout.spacer()

		with Layout.HBox():
			self.runbtn = self.Layout.button(u"빌드 후 실행",self.doReserveTestRun)
			self.nextbtn = self.Layout.button(u"다음",self.nextStep)#.setFixedHeight(20);

	def step4_GUI(self):
		self.Layout.label(u"<b>4. APK 작성</b>")
		self.Layout.hline();
		self.Layout.gap(3)

		self.Layout.spacer()

		self.progressText = self.Layout.label(u"설치 설명.")
		self.progress = self.Layout.addWidget(QProgressBar(self))
		
		self.Layout.spacer()

		self.nextbtn = self.Layout.button(u"종료",self.close)#.setFixedHeight(20);

		self.progress.setMaximum(100)
		self.progress.setMinimum(0)
		self.progress.setValue(0)

	def testRun_GUI(self):
		self.Layout.label(u"<b>APK 실행</b>")
		self.Layout.hline();
		self.Layout.gap(3)

		self.log = self.Layout.addWidget(QTextEdit(self))
		
		ADT_PATH = self.FindADT()
		if ADT_PATH : 
			ADBPATH = PJOIN(ADT_PATH,"platform-tools","adb.exe")
			out = PROCESS([ ADBPATH, "devices" ])
			if out : 
				self.log.setText(u"연결된 기기 검색 중 \n");
				self.log.setText(self.log.toPlainText()+out+"\n");

				self.startTestRun()
			else:
				print "Test Run Connect Error"
