# -*- coding: utf-8 -*-

import os
import sys

from PySide.QtGui import QDialog,QFileDialog,QMessageBox
from PySide.QtCore import QDir

from uic.Ui_NewProject import *
import setting

_Project_Default_Dir_ = ("build","resource","script","scene","symbol")

class NewProject(QDialog , Ui_NewProject):
    def __init__(self , parent=None):
        super(NewProject, self).__init__(parent)

        self.setupUi(self)
        self.ui_create.clicked.connect(self.uicall_create)
        self.ui_close.clicked.connect(self.uicall_close)
        self.ui_findWorkingDir.clicked.connect(self.uicall_findProject)

    def exec_(self,workingDir):
        self.ui_workingDir.setText(workingDir)
        self.ui_ProjectName.setFocus()
        super(NewProject,self).exec_()

    def uicall_create(self):
        pwd = self.ui_workingDir.text()
        if os.path.exists(pwd):
            fullpath = os.path.join(pwd,self.ui_ProjectName.text())
            if not os.path.exists(fullpath):
                os.makedirs(fullpath)

                for dir in _Project_Default_Dir_:
                    os.makedirs(os.path.join(fullpath,dir))

                proj = open(os.path.join(fullpath,"PROJ"),"w")
                proj.write("")
                proj.close()

                QMessageBox.information(self,"Designer",self.trUtf8("정상적으로 프로젝트가 생성되었습니다."))

                setting.setValue(setting.WorkingDir,pwd)

                self.close()
            else:
                QMessageBox.warning(self,"Designer",self.trUtf8("작업폴더에 동일한 프로젝트명의 폴더가 이미 있습니다.\n프로젝트명을 변경해주세요."))
        else:
            QMessageBox.warning(self,"Designer",self.trUtf8("폴더 경로가 존재하지 않습니다.\n작업 폴더를 먼저 생성해주세요."))

    def uicall_findProject(self):
        dir = QFileDialog.getExistingDirectory(parent = self,dir = "")
        if len(dir) > 0:
            self.ui_workingDir.setText(dir);

    def uicall_close(self):
        self.close()
