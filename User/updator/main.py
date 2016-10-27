# -*- coding: utf-8 -*-
import os
import shutil
import sys
import traceback
import os_encoding
import random
import requests

from GitUpdator import GitUpdator

import subprocess

from config import *
if config.__RELEASE__ == False : 
	sys.path.append("../Noriter")

from PySide.QtGui import *
from PySide.QtCore import *
from PySide.QtWebKit import *
from PySide.QtNetwork import *
from Noriter.views.NoriterMainWindow import *
from Noriter.UI.Layout import *
from Noriter.UI.Widget import Widget

import pycparser
import urllib2

'''
import admin

if not admin.isUserAdmin():
	admin.runAsAdmin()
'''

Error_Logger = open("ERROR_LOG.txt","w+")
sys.stderr = Error_Logger#sys.stdout

'''
if '__file__' in locals() or '__file__' in globals():
	_startup_cwd = os.path.dirname(os.path.dirname(__file__))
	if len(_startup_cwd) == 0 : 
		_startup_cwd = "."
else:
'''

#_startup_cwd = os.getcwd()
#_startup_cwd = _startup_cwd.decode(os_encoding.cp())

_startup_cwd = "."

def onerror(func, path, exc_info):
	"""
	Error handler for ``shutil.rmtree``.

	If the error is due to an access error (read only file)
	it attempts to add write permission and then retries.

	If the error is for another reason it re-raises the error.

	Usage : ``shutil.rmtree(path, onerror=onerror)``
	"""
	import stat
	if not os.access(path, os.W_OK):
		# Is the error an access error ?
		os.chmod(path, stat.S_IWUSR)
		func(path)
	else:
		raise

dist_root = os.path.join(_startup_cwd,"pini_update")
#dist_root = os.path.abspath(dist_root)

print "dist_root!!!",dist_root

class QProgressIndicator (QWidget):
	m_angle = None
	m_timerId = None
	m_delay = None
	m_displayedWhenStopped = None
	m_color = None

	def __init__ (self, parent):
		# Call parent class constructor first
		super(QProgressIndicator, self).__init__(parent)
		
		# Initialize Qt Properties
		self.setProperties()
		
		# Intialize instance variables
		self.m_angle = 0
		self.m_timerId = -1
		self.m_delay = 40
		self.m_displayedWhenStopped = False
		self.m_color = Qt.white 
		
		# Set size and focus policy
		self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
		self.setFocusPolicy(Qt.NoFocus)
		
		# Show the widget
		self.show()
		
	def animationDelay (self):
		return self.delay
		
	def isAnimated (self):
		return (self.m_timerId != -1)
		
	def isDisplayedWhenStopped (self):
		return self.displayedWhenStopped
		
	def getColor (self):
		return self.color
		
	def sizeHint (self):
		return QSize(20, 20)
	
	def startAnimation (self):
		self.m_angle = 0
		
		if self.m_timerId == -1:
			self.m_timerId = self.startTimer(self.m_delay)
		
	def stopAnimation (self):
		if self.m_timerId != -1:
			self.killTimer(self.m_timerId)
			
		self.m_timerId = -1
		self.update()
		
	def setAnimationDelay (self, delay):
		if self.m_timerId != -1:
			self.killTimer(self.m_timerId)
			
		self.m_delay = delay
		
		if self.m_timerId != -1:
			self.m_timerId = self.startTimer(self.m_delay)
		
	def setDisplayedWhenStopped (self, state):
		self.displayedWhenStopped = state
		self.update()
		
	def setColor (self, color):
		self.m_color = color
		self.update()
		
	def timerEvent (self, event):
		self.m_angle = (self.m_angle + 30) % 360
		self.update()
		
	def paintEvent (self, event):
		if (not self.m_displayedWhenStopped) and (not self.isAnimated()):
			return

		width = min(self.width(), self.height())
		
		painter = QPainter(self)
		painter.setRenderHint(QPainter.Antialiasing)
		
		outerRadius = (width - 1) * 0.5
		innerRadius = (width - 1) * 0.5 * 0.38
		
		capsuleHeight = outerRadius - innerRadius
		capsuleWidth	= capsuleHeight *.23 if (width > 32) else capsuleHeight *.35
		capsuleRadius = capsuleWidth / 2
		
		for i in range(0, 12):
			color = QColor(self.m_color)

			if self.isAnimated():
				color.setAlphaF(1.0 - (i / 12.0))
			else:
				color.setAlphaF(0.2)

			painter.setPen(Qt.NoPen)
			painter.setBrush(color)
			painter.save()
			painter.translate(self.rect().center())
			painter.rotate(self.m_angle - (i * 30.0))
			painter.drawRoundedRect(capsuleWidth * -0.5, (innerRadius + capsuleHeight) * -1, capsuleWidth, capsuleHeight, capsuleRadius, capsuleRadius)
			painter.restore()
			
	def setProperties (self):
		self.delay = Property(int, self.animationDelay, self.setAnimationDelay)
		self.displayedWhenStopped = Property(bool, self.isDisplayedWhenStopped, self.setDisplayedWhenStopped)
		self.color = Property(QColor, self.getColor, self.setColor)

def u(text):
	return unicode(text,"utf-8")

def restart():
	args = sys.argv[:]
	print('Re-spawning %s' % ' '.join(args))

	args.insert(0, sys.executable)
	if sys.platform == 'win32':
		args = ['"%s"' % arg for arg in args]

	os.chdir(_startup_cwd)
	os.execv(sys.executable, args)

def pini_start():
	os.chdir(dist_root)
	QProcess.startDetached("PiniEngine.exe")

class UpdateThread(QThread):
	updateFailed = Signal()
	updateText = Signal(str);
	updatePercent = Signal(int)

	def __init__(self,parent=None):
		QThread.__init__(self, parent)

	def progress(self,per):
		#print per
		self.updatePercent.emit(per)

	def run(self):
		#print dist_root,type(dist_root)
		updator = GitUpdator(dist_root,"https://github.com/nooslab/PiniEngine.git")
		updator.progress_perentage_callback = self.progress
		try:
			updator.update()
		except Exception, e:
			shutil.rmtree(dist_root,onerror=onerror)
			self.updateText.emit(str(e))
			
			traceback.print_exc(file=sys.stdout)
			try:
				updator.update()
			except Exception, e:
				print e
				traceback.print_exc(file=sys.stdout)
				self.updateText.emit(str(e))
				self.updateFailed.emit()


class QWebPageChrome(QWebPage) : 
	def __init__(self) : 
		super(QWebPageChrome,self).__init__()
	def userAgentForUrl(self,url):
		return "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.121 Safari/535.2"

class mainWidget(Widget):
	def __init__(self,parent=None):
		super(mainWidget,self).__init__(parent)

		self.progress = None;

		self.GUI()

		QNetworkProxyFactory.setUseSystemConfiguration(True);
		QWebSettings.globalSettings().setAttribute(QWebSettings.PluginsEnabled, True);
		QWebSettings.globalSettings().setAttribute(QWebSettings.AutoLoadImages, True);

		self.web.setPage(QWebPageChrome())
		
		self.web.settings().clearMemoryCaches()

		reqDomain = "http://nooslab.com/piniengine/toolNotice.php"
		reqBaseUrl = reqDomain#+"bbs/"
		self.web.setUrl(QUrl(reqBaseUrl))#+"board.php?bo_table=Menu_update"))
		self.web.setContentsMargins(0,0,0,0)

		self.onLoaded = False

		def loadFinished(ok):
			if self.onLoaded : 
				return 
			self.onLoaded = True 

			html = self.web.page().mainFrame().toHtml();
			html = html.replace("../",reqDomain)

			'''
			try:
				f = open("w.html","wb")
				f.write(html.encode("utf-8"))
				f.close()
			except Exception, e:
				pass
			'''
			
			self.web.setHtml(html)

			self.web.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
			#self.web.page().mainFrame().setScrollBarValue(Qt.Vertical, 193)
			#self.web.page().mainFrame().setScrollBarValue(Qt.Horizontal, 220)
			def _loaded_():
				self.onLoaded = False
			QTimer.singleShot(1000,_loaded_)

		self.web.loadFinished.connect(loadFinished)

		def linkClicked(url):
			QDesktopServices.openUrl(url);
		self.web.linkClicked.connect(linkClicked)


	@LayoutGUI
	def GUI(self):
		self.web = self.Layout.addWidget(QWebView(self))
		#self.label = self.Layout.label("")
		self.Layout.gap(3)
		with Layout.HBox() : 
			with Layout.VBox() :
				self.progress1 = self.Layout.addWidget(QProgressBar(self))
				self.Layout.gap(1)
				self.progress2 = self.Layout.addWidget(QProgressBar(self))

			self.Layout.gap(3)
			self.updateBtn = self.Layout.button(u("업데이트 및 실행"),self.clickUpdate)
			self.updateBtn.setFixedHeight(50)

	def updateBtnPos(self):
		return self.updateBtn.mapToParent(QPoint(0,0))

	def clickUpdate(self):
		self.progress = QProgressIndicator(self)
		self.progress.setAnimationDelay(70)
		self.progress.startAnimation()

		pt = self.updateBtnPos();
		self.progress.move(pt.x() + self.updateBtn.width()/2-15,pt.y())
		self.progress.resize(30,30)
		self.updateBtn.setDisabled(True)

		print dist_root

		def updatext(stext):
			pass
			#print stext
			#self.label.setText(self.label.text()+stext+"\n")

		self.call = 0
		def updatePercentage(per):
			self.progress1.setValue(per)
			self.progress2.setValue(self.call)

			self.call += random.randrange(2,4)
			if self.call > 100 :
				self.call = 0

		self.updateThread = UpdateThread()
		self.updateThread.finished.connect(self.updateFin)
		self.updateThread.updateFailed.connect(self.updateFailed)
		self.updateThread.updateText.connect(updatext)
		self.updateThread.updatePercent.connect(updatePercentage)
		self.updateThread.start()

	def resizeEvent(self,event):
		super(mainWidget,self).resizeEvent(event)
		if self.progress : 
			pt = self.updateBtnPos();
			self.progress.move(pt.x() + self.updateBtn.width()/2-15,pt.y())

	def updateFin(self):
		if self.progress : 
			self.progress.close()
			self.progress = None
			
			updator = GitUpdator(dist_root,"https://github.com/nooslab/PiniEngine.git")
			latest_ver = updator.latestCommitId()
			engine_ver = updator.commitId()

			if latest_ver != None and latest_ver != engine_ver:
				failed_message = u("업데이트가 제대로 진행되지 못했습니다.\n재부팅을 하신 뒤, 왼쪽 상단 메뉴의 설정-업데이트 삭제 를 선택하신 후,\n업데이트를 다시 진행해 주시기 바랍니다.\n\n이 메시지를 무시하시고 구 버전의 피니엔진을 실행하시려면, Yes 를 눌러주세요.")
				result = QMessageBox.warning(self,"pini",failed_message,QMessageBox.Yes | QMessageBox.No,QMessageBox.No)

				if result == QMessageBox.No:
					print "run canceled"
					return

			try:
				f = open("pini_ver.inf","w")
				f.write(engine_ver)
				f.close()
			except Exception, e:
				pass

			pini_start()
			app.quit()

	def updateFailed(self):
		self.progress.close()
		self.progress = None

		QMessageBox.warning(self,"pini",u("업데이트에 실패하였습니다. 네트워크 환경을 확인 해주세요.\n문제가 해결되지 않으면 관리자에게 문의해주세요."))		

if __name__ == "__main__":
	app = QApplication(sys.argv)

	css = QFile( "resource/QMain.css" )
	css.open( QFile.ReadOnly )

	styleSheet = css.readAll()
	app.setStyleSheet(unicode(styleSheet))

	css.close()

	m = NoriterMain()
	m.SetMain(mainWidget(m))
	m.resize(900,450)

	m.setWindowIcon(QIcon('resource/logoIcon64.png')) 

	def createAction(text,tip,call):
		newAct = QAction(u(text), NoriterMain());
		newAct.setStatusTip(u(tip));
		newAct.triggered.connect(call)
		return newAct

	def _clean_menu_():
		if os.path.isdir(dist_root) : 
			shutil.rmtree(dist_root,onerror=onerror)
			QMessageBox.information(NoriterMain(),"pini",u("초기화 되었습니다!"))
		else:
			QMessageBox.information(NoriterMain(),"pini",u("삭제할 파일이 없습니다."))		

	def _exit_menu_():
		NoriterMain().close()

	settingsMenu = m.menuBar().addMenu(u("설정(&S)"))
	settingsMenu.addAction(createAction("업데이트 삭제(&D)","업데이트를 받은 파일을 모두 초기화합니다.",_clean_menu_));
	settingsMenu.addAction(createAction("종료(&Q)","업데이터를 종료합니다.",_exit_menu_));

	#m.statusBar().addWidget(QLabel(u("현재버전 : "), m));
	#m.statusBar().addWidget(QLineEdit("&Download", m));

	update_ver = "0"
	try:
		f = open("update_ver.inf","r")
		update_ver = str(int(f.read()))
		f.close()
	except Exception, e:
		pass

	updator = GitUpdator(dist_root,"https://github.com/nooslab/PiniEngine.git")
	engine_ver = updator.commitId()
	if engine_ver == None : 
		engine_ver = u("없음")

	message = u("업데이터 버전 : ")+update_ver+u(" | 엔진 버전 : ")+engine_ver+u(" ")
	m.statusBar().addWidget(QLabel(message,m))

	#sys.stderr.write("aaaaaaaaaaa")

	_exit_ = app.exec_()
	##################
	Error_Logger.close()

	check = False
	with open('ERROR_LOG.txt', 'rb') as f : 
		if len(f.read()) > 0 : 
			check=True
	
	if check : 
		r = requests.post('http://nooslab.com/piniengine/errlog/upload.php?p=1', files={'file': ('log.txt', open('ERROR_LOG.txt', 'rb'), 'text/plain', {'Expires': '0'})})
		print r.text
		print r.status_code
		if r.status_code == 200 : 
			os.remove("ERROR_LOG.txt")
	##################
	sys.exit(_exit_)

