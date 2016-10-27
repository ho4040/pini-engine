# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Dev\DevTool\User\Desinger-ui\LayerListDock.ui'
#
# Created: Thu Jul 17 15:51:14 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_LayerList(object):
    def setupUi(self, LayerList):
        LayerList.setObjectName("LayerList")
        LayerList.resize(653, 561)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.verticalLayout.setObjectName("verticalLayout")
        self.ui_layerList_scrollArea = QtGui.QScrollArea(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_layerList_scrollArea.sizePolicy().hasHeightForWidth())
        self.ui_layerList_scrollArea.setSizePolicy(sizePolicy)
        self.ui_layerList_scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.ui_layerList_scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.ui_layerList_scrollArea.setWidgetResizable(True)
        self.ui_layerList_scrollArea.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.ui_layerList_scrollArea.setObjectName("ui_layerList_scrollArea")
        self.ui_ListContents = QtGui.QWidget()
        self.ui_ListContents.setGeometry(QtCore.QRect(0, 0, 628, 406))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_ListContents.sizePolicy().hasHeightForWidth())
        self.ui_ListContents.setSizePolicy(sizePolicy)
        self.ui_ListContents.setStyleSheet("")
        self.ui_ListContents.setObjectName("ui_ListContents")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.ui_ListContents)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.verticalLayout_2.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.ui_ListVBox = QtGui.QVBoxLayout()
        self.ui_ListVBox.setSpacing(2)
        self.ui_ListVBox.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.ui_ListVBox.setObjectName("ui_ListVBox")
        spacerItem = QtGui.QSpacerItem(20, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.ui_ListVBox.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.ui_ListVBox)
        self.ui_layerList_scrollArea.setWidget(self.ui_ListContents)
        self.verticalLayout.addWidget(self.ui_layerList_scrollArea)
        self.ui_openTestScene = QtGui.QPushButton(self.dockWidgetContents)
        self.ui_openTestScene.setObjectName("ui_openTestScene")
        self.verticalLayout.addWidget(self.ui_openTestScene)
        self.ui_testScene1Select = QtGui.QPushButton(self.dockWidgetContents)
        self.ui_testScene1Select.setObjectName("ui_testScene1Select")
        self.verticalLayout.addWidget(self.ui_testScene1Select)
        self.ui_testScene2Select = QtGui.QPushButton(self.dockWidgetContents)
        self.ui_testScene2Select.setObjectName("ui_testScene2Select")
        self.verticalLayout.addWidget(self.ui_testScene2Select)
        self.ui_layerAdd = QtGui.QPushButton(self.dockWidgetContents)
        self.ui_layerAdd.setObjectName("ui_layerAdd")
        self.verticalLayout.addWidget(self.ui_layerAdd)
        self.ui_layerDelete = QtGui.QPushButton(self.dockWidgetContents)
        self.ui_layerDelete.setObjectName("ui_layerDelete")
        self.verticalLayout.addWidget(self.ui_layerDelete)
        LayerList.setWidget(self.dockWidgetContents)

        self.retranslateUi(LayerList)
        QtCore.QMetaObject.connectSlotsByName(LayerList)

    def retranslateUi(self, LayerList):
        LayerList.setWindowTitle(QtGui.QApplication.translate("LayerList", "레이어 리스트", None, QtGui.QApplication.UnicodeUTF8))
        self.ui_openTestScene.setText(QtGui.QApplication.translate("LayerList", "testSceneList 열기", None, QtGui.QApplication.UnicodeUTF8))
        self.ui_testScene1Select.setText(QtGui.QApplication.translate("LayerList", "testScene1 선택", None, QtGui.QApplication.UnicodeUTF8))
        self.ui_testScene2Select.setText(QtGui.QApplication.translate("LayerList", "testScene2 선택", None, QtGui.QApplication.UnicodeUTF8))
        self.ui_layerAdd.setText(QtGui.QApplication.translate("LayerList", "레이어 추가", None, QtGui.QApplication.UnicodeUTF8))
        self.ui_layerDelete.setText(QtGui.QApplication.translate("LayerList", "레이어 삭제", None, QtGui.QApplication.UnicodeUTF8))

