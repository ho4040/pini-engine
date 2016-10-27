# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Dev\DevTool\User\Desinger-ui\Launcher.ui'
#
# Created: Tue Jul 22 14:30:45 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Launcher(object):
    def setupUi(self, Launcher):
        Launcher.setObjectName("Launcher")
        Launcher.setWindowModality(QtCore.Qt.ApplicationModal)
        Launcher.resize(400, 300)
        self.verticalLayout_3 = QtGui.QVBoxLayout(Launcher)
        self.verticalLayout_3.setSpacing(2)
        self.verticalLayout_3.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QtGui.QLabel(Launcher)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.ui_ProjectList = QtGui.QListView(Launcher)
        self.ui_ProjectList.setObjectName("ui_ProjectList")
        self.verticalLayout_2.addWidget(self.ui_ProjectList)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtGui.QLabel(Launcher)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.ui_WorkingDir = QtGui.QLineEdit(Launcher)
        self.ui_WorkingDir.setReadOnly(True)
        self.ui_WorkingDir.setObjectName("ui_WorkingDir")
        self.horizontalLayout.addWidget(self.ui_WorkingDir)
        self.ui_FindWorkingDir = QtGui.QPushButton(Launcher)
        self.ui_FindWorkingDir.setObjectName("ui_FindWorkingDir")
        self.horizontalLayout.addWidget(self.ui_FindWorkingDir)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.ui_OpenProject = QtGui.QPushButton(Launcher)
        self.ui_OpenProject.setObjectName("ui_OpenProject")
        self.verticalLayout.addWidget(self.ui_OpenProject)
        self.ui_NewProject = QtGui.QPushButton(Launcher)
        self.ui_NewProject.setObjectName("ui_NewProject")
        self.verticalLayout.addWidget(self.ui_NewProject)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.ui_Update = QtGui.QPushButton(Launcher)
        self.ui_Update.setObjectName("ui_Update")
        self.verticalLayout.addWidget(self.ui_Update)
        self.ui_Close = QtGui.QPushButton(Launcher)
        self.ui_Close.setObjectName("ui_Close")
        self.verticalLayout.addWidget(self.ui_Close)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Launcher)
        QtCore.QMetaObject.connectSlotsByName(Launcher)
        Launcher.setTabOrder(self.ui_ProjectList, self.ui_WorkingDir)
        Launcher.setTabOrder(self.ui_WorkingDir, self.ui_FindWorkingDir)
        Launcher.setTabOrder(self.ui_FindWorkingDir, self.ui_OpenProject)
        Launcher.setTabOrder(self.ui_OpenProject, self.ui_NewProject)
        Launcher.setTabOrder(self.ui_NewProject, self.ui_Update)
        Launcher.setTabOrder(self.ui_Update, self.ui_Close)

    def retranslateUi(self, Launcher):
        Launcher.setWindowTitle(QtGui.QApplication.translate("Launcher", "Launcher", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Launcher", "프로젝트 리스트", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Launcher", "경로", None, QtGui.QApplication.UnicodeUTF8))
        self.ui_FindWorkingDir.setText(QtGui.QApplication.translate("Launcher", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.ui_OpenProject.setText(QtGui.QApplication.translate("Launcher", "프로젝트 열기 (&O)", None, QtGui.QApplication.UnicodeUTF8))
        self.ui_NewProject.setText(QtGui.QApplication.translate("Launcher", "새로운 프로젝트 (&N)", None, QtGui.QApplication.UnicodeUTF8))
        self.ui_Update.setText(QtGui.QApplication.translate("Launcher", "업데이트 (&U)", None, QtGui.QApplication.UnicodeUTF8))
        self.ui_Close.setText(QtGui.QApplication.translate("Launcher", "종료 (X)", None, QtGui.QApplication.UnicodeUTF8))

