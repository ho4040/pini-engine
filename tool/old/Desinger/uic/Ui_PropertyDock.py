# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/choiyoung/Desktop/works/DevTool/User/Desinger-ui/PropertyDock.ui'
#
# Created: Thu Jul 17 12:31:20 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_PropertyDock(object):
    def setupUi(self, PropertyDock):
        PropertyDock.setObjectName("PropertyDock")
        PropertyDock.resize(375, 406)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setMinimumSize(QtCore.QSize(300, 0))
        self.dockWidgetContents.setBaseSize(QtCore.QSize(0, 0))
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.ui_ToolBox = QtGui.QToolBox(self.dockWidgetContents)
        self.ui_ToolBox.setObjectName("ui_ToolBox")
        self.page = QtGui.QWidget()
        self.page.setGeometry(QtCore.QRect(0, 0, 375, 315))
        self.page.setObjectName("page")
        self.ui_ToolBox.addItem(self.page, "")
        self.verticalLayout.addWidget(self.ui_ToolBox)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(17, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.ui_AddComponent = QtGui.QPushButton(self.dockWidgetContents)
        self.ui_AddComponent.setObjectName("ui_AddComponent")
        self.horizontalLayout.addWidget(self.ui_AddComponent)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        PropertyDock.setWidget(self.dockWidgetContents)

        self.retranslateUi(PropertyDock)
        self.ui_ToolBox.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(PropertyDock)

    def retranslateUi(self, PropertyDock):
        PropertyDock.setWindowTitle(QtGui.QApplication.translate("PropertyDock", "Property", None, QtGui.QApplication.UnicodeUTF8))
        self.ui_ToolBox.setItemText(self.ui_ToolBox.indexOf(self.page), QtGui.QApplication.translate("PropertyDock", "Page 1", None, QtGui.QApplication.UnicodeUTF8))
        self.ui_AddComponent.setText(QtGui.QApplication.translate("PropertyDock", "요소 추가", None, QtGui.QApplication.UnicodeUTF8))

