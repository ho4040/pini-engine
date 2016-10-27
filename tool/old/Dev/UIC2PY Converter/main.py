import sys
import os
import ntpath
import json

from PySide.QtGui import *
from PySide.QtCore import *
from ui_mainwindow import Ui_MainWindow

toolName = "UIC2PY Converter"
settings = QSettings("Nooslab", toolName)

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        global settings,toolName
        super(MainWindow, self).__init__(parent)

        self.setupUi(self)

        self.input_find.clicked.connect(self.findInputDir)
        self.output_find.clicked.connect(self.findOutputDir)
        self.start.clicked.connect(self.startConvert)

        self.input.setText(settings.value("%s/in"%toolName))
        self.output.setText(settings.value("%s/out"%toolName))

        self.setWindowTitle("UIC2PY Converter")

    def findInputDir(self):
        dir = QFileDialog.getExistingDirectory(parent = self,dir = self.input.text())
        if len(dir) > 0:
            self.input.setText(dir)

    def findOutputDir(self):
        dir = QFileDialog.getExistingDirectory(parent = self,dir = self.output.text())
        if len(dir) > 0:
            self.output.setText(dir)

    def startConvert(self):
        for dirname, dirnames, filenames in os.walk(self.input.text()):
            for filename in filenames:
                if '.ui' in filename:
                    currentFileName = os.path.join(dirname, filename)
                    
                    output = self.output.text()+"/Ui_"+filename.replace(".ui", ".py")
                    directory = os.path.dirname(output)
                    
                    if not os.path.exists(directory):
                        os.makedirs(directory)

                    importFile = self.output.text()+"/__init__.py";
                    if not os.path.exists(importFile):
                        f = open(importFile, 'w')
                        f.write("__author__ = 'Nooslab'") 
                        f.close()


                    execuateCommand = "pyside-uic \""+currentFileName+"\" -o \"" + output +"\""
                    os.system(execuateCommand)

                    self.textEdit.setPlainText(self.textEdit.toPlainText()+execuateCommand+"\n")

        self.textEdit.setPlainText(self.textEdit.toPlainText()+"\n\n convert finished!")

    def closeEvent(self, event):
        global settings,toolName
        settings.setValue("%s/in"%toolName,self.input.text())
        settings.setValue("%s/out"%toolName,self.output.text())


        QMainWindow.closeEvent(self, event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = MainWindow()
    frame.show()
    app.exec_()
    