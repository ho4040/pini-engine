# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/choiyoung/Desktop/works/DevTool/User/Desinger-ui/NewProject.ui'
#
# Created: Thu Jul 17 12:31:20 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_NewProject(object):
    def setupUi(self, NewProject):
        NewProject.setObjectName("NewProject")
        NewProject.setWindowModality(QtCore.Qt.ApplicationModal)
        NewProject.resize(495, 112)
        self.verticalLayout = QtGui.QVBoxLayout(NewProject)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSpacing(3)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(NewProject)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.label_3 = QtGui.QLabel(NewProject)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.label_2 = QtGui.QLabel(NewProject)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.ui_workingDir = QtGui.QLineEdit(NewProject)
        self.ui_workingDir.setObjectName("ui_workingDir")
        self.gridLayout.addWidget(self.ui_workingDir, 2, 1, 1, 1)
        self.ui_ProjectName = QtGui.QLineEdit(NewProject)
        self.ui_ProjectName.setObjectName("ui_ProjectName")
        self.gridLayout.addWidget(self.ui_ProjectName, 1, 1, 1, 1)
        self.ui_findWorkingDir = QtGui.QPushButton(NewProject)
        self.ui_findWorkingDir.setObjectName("ui_findWorkingDir")
        self.gridLayout.addWidget(self.ui_findWorkingDir, 2, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.ui_create = QtGui.QPushButton(NewProject)
        self.ui_create.setObjectName("ui_create")
        self.horizontalLayout.addWidget(self.ui_create)
        self.ui_close = QtGui.QPushButton(NewProject)
        self.ui_close.setObjectName("ui_close")
        self.horizontalLayout.addWidget(self.ui_close)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(NewProject)
        QtCore.QMetaObject.connectSlotsByName(NewProject)

    def retranslateUi(self, NewProject):
        NewProject.setWindowTitle(QtGui.QApplication.translate("NewProject", "새로운 프로젝트 생성", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("NewProject", "새로운 프로젝트 생성", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("NewProject", "작업 폴더", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("NewProject", "프로젝트 명", None, QtGui.QApplication.UnicodeUTF8))
        self.ui_findWorkingDir.setText(QtGui.QApplication.translate("NewProject", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.ui_create.setText(QtGui.QApplication.translate("NewProject", "생성", None, QtGui.QApplication.UnicodeUTF8))
        self.ui_close.setText(QtGui.QApplication.translate("NewProject", "취소", None, QtGui.QApplication.UnicodeUTF8))

