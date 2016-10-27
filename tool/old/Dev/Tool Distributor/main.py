import sys
import os
import time
import urllib2
import httplib
import zipfile
import json

import requests
from requests_toolbelt import MultipartEncoder

from PySide.QtGui import *
from PySide.QtCore import *
from PySide.QtNetwork import *
from mainwindow import Ui_MainWindow

toolName = "Tool Distributor"
settings = QSettings("Nooslab", toolName)

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        global settings,toolName
        super(MainWindow, self).__init__(parent)

        self.setupUi(self)

        self.setWindowTitle(toolName)

        self.hostName_editBox.setText(settings.value("%s/hostName"%toolName))
        self.port_editbox.setText(settings.value("%s/port"%toolName))
        self.setupPy_EditBox.setText(settings.value("%s/setupPyPath"%toolName))

        self.majorVersion_editBox.setText(settings.value("%s/majorVersion"%toolName))
        self.minorVersion_editBox.setText(settings.value("%s/minorVersion"%toolName))
        self.trivialVersion_editBox.setText(settings.value("%s/trivialVersion"%toolName))

        self.pathDialog_button.released.connect(self.pathDialog_button_onClicked)
        self.upload_button.released.connect(self.upload_button_onClicked)

        self.versionRefresh_button.clicked.connect(self.versionRefresh_button_onClicked)

        # Set 'hostName' EditBox Completer
        completerArray = []
        size = settings.beginReadArray("%s/hostName_completer"%toolName)
        print "settings.beginReadArray(\"/hostName_completer\"toolName) size : %d" %size
        for i in range(size):
            settings.setArrayIndex(i)
            print settings.value("value")
            completerArray.append(settings.value("value"))
        settings.endArray()

        defaultCompleter = QCompleter(completerArray,self)
        defaultCompleter.setCaseSensitivity(Qt.CaseInsensitive)
        defaultCompleter.setCompletionMode(QCompleter.PopupCompletion)

        self.hostName_editBox.setCompleter(defaultCompleter)

        # Set 'port' EditBox Completer
        completerArray = []

        size = settings.beginReadArray("%s/port_completer"%toolName)
        print "settings.beginReadArray(\"/port_completer\"toolName) size : %d" %size
        for i in range(size):
            settings.setArrayIndex(i)
            print settings.value("value")
            completerArray.append(settings.value("value"))
        settings.endArray()

        defaultCompleter = QCompleter(completerArray,self)
        defaultCompleter.setCaseSensitivity(Qt.CaseInsensitive)
        defaultCompleter.setCompletionMode(QCompleter.PopupCompletion)

        self.port_editbox.setCompleter(defaultCompleter)

        # Set 'setup.py' EditBox Completer
        completerArray = []

        size = settings.beginReadArray("%s/setupPy_completer"%toolName)
        for i in range(size):
            settings.setArrayIndex(i)
            completerArray.append(settings.value("value"))
        settings.endArray()

        defaultCompleter = QCompleter(completerArray,self)
        defaultCompleter.setCaseSensitivity(Qt.CaseInsensitive)
        defaultCompleter.setCompletionMode(QCompleter.PopupCompletion)
        
        self.setupPy_EditBox.setCompleter(defaultCompleter)


    def pathDialog_button_onClicked(self):
        path,filter = QFileDialog.getOpenFileName(parent = self,dir = self.setupPy_EditBox.text(),filter="*.py")

        if len(path) > 0:
            self.setupPy_EditBox.setText(path)

    def toolPackaging(self):
        setupPyPath = self.setupPy_EditBox.text()

        self.output_editBox.append("tool packaging...")
        #set working directory
        setupPyDir = os.path.dirname(setupPyPath)
        os.chdir(setupPyDir)

        #set _property.py (version info)
        propertyPyPath = os.path.join(setupPyDir,"_property_.py")
        if os.path.isfile(propertyPyPath):
            os.remove(propertyPyPath)

        propertyDic = {
            "VERSION": self.getLatestVersionStr()
        }

        propertyJson = json.dumps(propertyDic, sort_keys=True,indent=4,separators=(',', ': '))
        propertyStr  ="___PROPERTY___ = %s" % propertyJson

        propertyFile = open('_property_.py', 'w')
        propertyFile.write(propertyStr)

        propertyFile.write(os.linesep)
        propertyCode = ["def __getMetaProperty(key):",
        "\ttry:",
        "\t\treturn ___PROPERTY___[key]",
        "\texcept Exception:",
        "\t\treturn None"]

        getMetaPropertyFunStr = os.linesep.join(propertyCode)
        propertyFile.write(getMetaPropertyFunStr)

        propertyFile.close()

        #execute py2exe
        execuateCommand = "python \"%s\" py2exe" % setupPyPath
        result = os.system(execuateCommand)

        if result != 0:
            alertMessageBox = QMessageBox()
            alertMessageBox.setWindowTitle("error")
            alertMessageBox.setText("py2exe failed! result code: %s"%str(result))
            alertMessageBox.exec_()
            return False

        self.output_editBox.append("tool packaging complete...")
        return True

    def fileCompress(self):
        self.output_editBox.append("package file compressing...")
        def zipInDirectory(path, zip):
            basePathNum = len(path.split(os.sep))

            for root, dirs, files in os.walk(path):
                for file in files:
                    filePath   = os.path.join(root, file).split(os.sep)
                    pathByRoot = os.path.join(*filePath[basePathNum:])
                    zip.write(pathByRoot)

        setupPyPath    = self.setupPy_EditBox.text()

        setupPyPathDir = os.path.dirname(setupPyPath)
        targetDir      = os.path.join(setupPyPathDir,"dist")
        outputDir      = os.path.join(setupPyPathDir,"package_output")
        outputPath     = os.path.join(outputDir,time.strftime("%Y%m%d_%H_%M_%S.zip"))

        if not os.path.isdir(outputDir):
            os.mkdir(outputDir)

        os.chdir(targetDir)
        zipf = zipfile.ZipFile(outputPath,'w', zipfile.ZIP_DEFLATED)
        zipInDirectory(targetDir, zipf)
        zipf.close()
        os.chdir(setupPyPathDir)

        self.output_editBox.append("package file compressing complete...")
        return True,outputPath
    def uploadZipFile(self,archiveFilePath):
        url   = self.hostName_editBox.text()
        port  = self.port_editbox.text()

        self.output_editBox.append("upload starting...")

        head, tail = os.path.split(archiveFilePath)

        requestUrl = QUrl()
        requestUrl.setUrl(url)
        requestUrl.setPort(int(port))

        files = {'file': (tail, open(archiveFilePath, 'rb'), 'application/x-zip-compressed')}
        print requestUrl.toString()
        r = requests.post(requestUrl.toString(), files = files, data = {'version': self.getLatestVersionStr()})

        self.output_editBox.append("----- upload request response -----")
        self.output_editBox.append(json.dumps(r.text,sort_keys=True,indent=4,separators=(',', ':')))
        self.output_editBox.append("-----------------------------------")
        self.output_editBox.append("upload succeed!")
        return True

    def saveCompleter(self):
        print "call saveCompleter!!"
        global settings,toolName
        hostNameCompleter = self.hostName_editBox.completer()
        portCompleter     = self.port_editbox.completer()
        setupPyCompleter  = self.setupPy_EditBox.completer()

        if hostNameCompleter:
            print "hostNameCompleter is not None!"
            oldList = hostNameCompleter.model().stringList()
            isExist = self.hostName_editBox.text() in oldList

            if not isExist:
                oldList.append(self.hostName_editBox.text())
                hostNameCompleter.setModel(QStringListModel(oldList))

            print "isExist : " + str(isExist)
            print "len(hostNameCompleter) : %d" % len(oldList)

            settings.beginWriteArray("%s/hostName_completer"%toolName)
            for idx,item in enumerate(oldList):
                settings.setArrayIndex(idx)
                settings.setValue("value",item)
            settings.endArray()

        if portCompleter:
            print "portCompleter is not None!"
            oldList = portCompleter.model().stringList()
            isExist = self.port_editbox.text() in oldList

            if not isExist:
                oldList.append(self.port_editbox.text())
                portCompleter.setModel(QStringListModel(oldList))

            print "isExist : " + str(isExist)
            print "len(portCompleter) : %d" % len(oldList)

            settings.beginWriteArray("%s/port_completer"%toolName)
            for idx,item in enumerate(oldList):
                settings.setArrayIndex(idx)
                settings.setValue("value",item)
            settings.endArray()

        if setupPyCompleter:
            print "setupPyCompleter is not None!"
            oldList = setupPyCompleter.model().stringList()
            isExist = self.setupPy_EditBox.text() in oldList

            if not isExist:
                oldList.append(self.setupPy_EditBox.text())
                setupPyCompleter.setModel(QStringListModel(oldList))

            print "isExist : " + str(isExist)
            print "len(setupPyCompleter) : %d" % len(oldList)

            settings.beginWriteArray("%s/setupPy_completer"%toolName)
            for idx,item in enumerate(oldList):
                print str(idx) + " " + str(item)
                settings.setArrayIndex(idx)
                settings.setValue("value",item)
            settings.endArray()

    def isReady(self):
        alertMessage = []

        url         = self.hostName_editBox.text()
        port        = self.port_editbox.text()
        setupPyPath = self.setupPy_EditBox.text()

        if not len(url) > 0:
            alertMessage.append("set your host name!")
        if not len(port) > 0:
            alertMessage.append("set your port!")
        else:
            if not port.isdigit():
                alertMessage.append("port must be only natural number!")

        if not len(setupPyPath) > 0:
            alertMessage.append("set your setup.py path!")
        else:
            if not os.path.isfile(setupPyPath):
                self.setupPy_EditBox.setText("")
                alertMessage.append("setup.py filepath:\"%s\" is not an existing regular file!" % setupPyPath)

        majorVersion   = self.majorVersion_editBox.text()
        minorVersion   = self.minorVersion_editBox.text()
        trivialVersion = self.trivialVersion_editBox.text()

        if not majorVersion.isdigit():
            alertMessage.append("majorVersion must be only natural number!")
            self.majorVersion_editBox.setText("")
        if not minorVersion.isdigit():
            alertMessage.append("minorVersion must be only natural number!")
            self.minorVersion_editBox.setText("")
        if not trivialVersion.isdigit():
            alertMessage.append("trivialVersion must be only natural number!")
            self.trivialVersion_editBox.setText("")

        if len(alertMessage) > 0:
            QMessageBox.warning(self,"error",os.linesep.join(alertMessage))
            return False
        return True

    def getLatestVersion(self):
        majorVersion = "1"
        minorVersion = "0"
        trivialVersion = "0"

        alertMessage = []

        url  = self.hostName_editBox.text()
        port = self.port_editbox.text()

        requestUrl = QUrl()

        if len(url) > 0:
            requestUrl.setUrl(url)
        else:
            alertMessage.append("set your host name!")
        if len(port) > 0:
            requestUrl.setPort(int(port))
        else:
            alertMessage.append("set your port!")

        if len(alertMessage) > 0:
            QMessageBox.warning(self,"error",os.linesep.join(alertMessage))

        print requestUrl.host()

        #r = requests.get('https://github.com/timeline.json')

        return [majorVersion,minorVersion,trivialVersion]

    def getLatestVersionStr(self):
        return str('.'.join(self.getLatestVersion()))

    def versionRefresh_button_onClicked(self):
        versions = self.getLatestVersion()

        alertMessage = []

        majorVersion   = self.majorVersion_editBox.text()
        minorVersion   = self.minorVersion_editBox.text()
        trivialVersion = self.trivialVersion_editBox.text()

        majorVersionIsEmpty   = len(majorVersion) == 0
        minorVersionIsEmpty   = len(minorVersion) == 0
        trivialVersionIsEmpty = len(trivialVersion) == 0

        if not majorVersionIsEmpty:
            if not majorVersion.isdigit():
                alertMessage.append("majorVersion must be only natural number!")
                self.majorVersion_editBox.setText("")
            else:
                if int(majorVersion) <= int(versions[0]):
                    self.majorVersion_editBox.setText(versions[0])
        else:
            self.majorVersion_editBox.setText(versions[0])

        if not minorVersionIsEmpty:
            if not minorVersion.isdigit():
                alertMessage.append("minorVersion must be only natural number!")
                self.minorVersion_editBox.setText("")
            else:
                if int(minorVersion) <= int(versions[1]):
                    self.minorVersion_editBox.setText(versions[1])
        else:
            self.minorVersion_editBox.setText(versions[1])

        if not trivialVersionIsEmpty:
            if not trivialVersion.isdigit():
                alertMessage.append("trivialVersion must be only natural number!")
                self.trivialVersion_editBox.setText("")
            else:
                if int(trivialVersion) <= int(versions[2]):
                    self.trivialVersion_editBox.setText(str(int(versions[2]) + 1))
        else:
            self.trivialVersion_editBox.setText(str(int(versions[2]) + 1))

        if len(alertMessage) > 0:
            QMessageBox.warning(self,"error",os.linesep.join(alertMessage))
        else:
            self.saveCompleter()

    def upload_button_onClicked(self):
        def work():
            if not self.isReady():
                return False
            if not self.toolPackaging():
                return False

            archiveResult,archiveFilePath = self.fileCompress()
            if archiveResult:
                if not self.uploadZipFile(archiveFilePath):
                    return False

            self.saveCompleter()
            return True
        while True:
            result = work()
            break

    def closeEvent(self, event):
        global settings,toolName
        settings.setValue("%s/hostName"%toolName,self.hostName_editBox.text())
        settings.setValue("%s/port"%toolName,self.port_editbox.text())
        settings.setValue("%s/setupPyPath"%toolName,self.setupPy_EditBox.text())

        settings.setValue("%s/majorVersion"%toolName,self.majorVersion_editBox.text())
        settings.setValue("%s/minorVersion"%toolName,self.minorVersion_editBox.text())
        settings.setValue("%s/trivialVersion"%toolName,self.trivialVersion_editBox.text())

        QMainWindow.closeEvent(self, event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = MainWindow()
    frame.show()
    app.exec_()