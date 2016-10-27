# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/choiyoung/Desktop/works/DevTool/User/Desinger-ui/BrowserDock.ui'
#
# Created: Thu Jul 17 12:31:20 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_BrowserDock(object):
    def setupUi(self, BrowserDock):
        BrowserDock.setObjectName("BrowserDock")
        BrowserDock.resize(792, 211)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(BrowserDock.sizePolicy().hasHeightForWidth())
        BrowserDock.setSizePolicy(sizePolicy)
        BrowserDock.setMinimumSize(QtCore.QSize(82, 108))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.ui_Explorer = QtGui.QTreeView(self.dockWidgetContents)
        self.ui_Explorer.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_Explorer.sizePolicy().hasHeightForWidth())
        self.ui_Explorer.setSizePolicy(sizePolicy)
        self.ui_Explorer.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.ui_Explorer.setBaseSize(QtCore.QSize(0, 0))
        self.ui_Explorer.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui_Explorer.setLineWidth(1)
        self.ui_Explorer.setObjectName("ui_Explorer")
        self.verticalLayout.addWidget(self.ui_Explorer)
        BrowserDock.setWidget(self.dockWidgetContents)

        self.retranslateUi(BrowserDock)
        QtCore.QMetaObject.connectSlotsByName(BrowserDock)

    def retranslateUi(self, BrowserDock):
        BrowserDock.setWindowTitle(QtGui.QApplication.translate("BrowserDock", "프로젝트 탐색기", None, QtGui.QApplication.UnicodeUTF8))

