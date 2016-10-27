#-*- coding: utf-8 -*-

import os
import sys

from PySide.QtGui import QDialog,QFileDialog
from PySide.QtCore import QDir
from uic.Ui_Launcher import *

import setting

from windows.NewProject import NewProject

class Launcher(QDialog , Ui_Launcher):

    class WorkingDirListModel(QtCore.QAbstractListModel):
        def __init__(self, contents):
            super(Launcher.WorkingDirListModel, self).__init__()
            self.contents = contents

        def rowCount(self, parent):
            return len(self.contents)

        def data(self, index, role):
            if role == QtCore.Qt.DisplayRole:
                return str(self.contents[index.row()])

    def __init__(self , parent=None):
        super(Launcher, self).__init__(parent)

        self.setupUi(self)
        self.ui_NewProject.clicked.connect(self.uicall_newProject)
        self.ui_Update.clicked.connect(self.uicall_update)
        self.ui_Close.clicked.connect(self.uicall_closeProject)
        self.ui_FindWorkingDir.clicked.connect(self.uicall_findWorkingDir)

        self.ui_ProjectList.doubleClicked.connect(self.openProject)
        self.ui_OpenProject.clicked.connect(self.openProject)

        self.loadingWorkingDir()

        self.selectedProject = None;

    def openProject(self):
        selectedText = self.ui_ProjectList.model().data(self.ui_ProjectList.currentIndex(),QtCore.Qt.DisplayRole)
        if len(selectedText) > 0 :
            self.selectedProject = os.path.join(self.ui_WorkingDir.text(),selectedText)
            self.close()

    def loadingWorkingDir(self):
        cwd = setting.value(setting.WorkingDir)
        if not cwd:
            cwd = os.getcwd()
        self.ui_WorkingDir.setText(cwd)

        projs = []
        for dirname in os.listdir(cwd):
            if os.path.exists(os.path.join(cwd,dirname,"PROJ")):
                projs.append(dirname)

        self.ui_ProjectList.setModel(Launcher.WorkingDirListModel(projs))

    def uicall_findWorkingDir(self):
        dir = QFileDialog.getExistingDirectory(self,"Designer","Working Directory")
        if len(dir) > 0:
            setting.setValue(setting.WorkingDir,dir)
            self.loadingWorkingDir()

    def uicall_newProject(self):
        NewProject(self).exec_(self.ui_WorkingDir.text())

        self.loadingWorkingDir()

    def uicall_update(self):
        print("uicall_update")

    def uicall_closeProject(self):
        self.close()

    def exec_(self):
        super(Launcher,self).exec_()
        return self.selectedProject

    def closeEvent(self,event):
        setting.setValue(setting.WorkingDir,self.ui_WorkingDir.text())

