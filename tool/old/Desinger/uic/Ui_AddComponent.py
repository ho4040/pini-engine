# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/choiyoung/Desktop/works/DevTool/User/Desinger-ui/AddComponent.ui'
#
# Created: Thu Jul 17 12:31:20 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_AddComponent(object):
    def setupUi(self, AddComponent):
        AddComponent.setObjectName("AddComponent")
        AddComponent.resize(407, 37)
        AddComponent.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(AddComponent)
        self.verticalLayout.setSpacing(1)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.ui_Edit = QtGui.QComboBox(AddComponent)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_Edit.sizePolicy().hasHeightForWidth())
        self.ui_Edit.setSizePolicy(sizePolicy)
        self.ui_Edit.setEditable(True)
        self.ui_Edit.setObjectName("ui_Edit")
        self.horizontalLayout.addWidget(self.ui_Edit)
        self.ui_add = QtGui.QPushButton(AddComponent)
        self.ui_add.setObjectName("ui_add")
        self.horizontalLayout.addWidget(self.ui_add)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(AddComponent)
        QtCore.QMetaObject.connectSlotsByName(AddComponent)

    def retranslateUi(self, AddComponent):
        AddComponent.setWindowTitle(QtGui.QApplication.translate("AddComponent", "요소 추가", None, QtGui.QApplication.UnicodeUTF8))
        self.ui_add.setText(QtGui.QApplication.translate("AddComponent", "추가", None, QtGui.QApplication.UnicodeUTF8))

