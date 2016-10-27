# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/choiyoung/Desktop/works/DevTool/User/Desinger-ui/UCSprite.ui'
#
# Created: Thu Jul 17 12:31:21 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_UCSprite(object):
    def setupUi(self, UCSprite):
        UCSprite.setObjectName("UCSprite")
        UCSprite.resize(357, 161)
        self.verticalLayout = QtGui.QVBoxLayout(UCSprite)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_5 = QtGui.QLabel(UCSprite)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout.addWidget(self.label_5)
        self.ui_Src = QtGui.QLineEdit(UCSprite)
        self.ui_Src.setReadOnly(True)
        self.ui_Src.setObjectName("ui_Src")
        self.horizontalLayout.addWidget(self.ui_Src)
        self.ui_find = QtGui.QPushButton(UCSprite)
        self.ui_find.setObjectName("ui_find")
        self.horizontalLayout.addWidget(self.ui_find)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(UCSprite)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.ui_R = QtGui.QLineEdit(UCSprite)
        self.ui_R.setObjectName("ui_R")
        self.gridLayout.addWidget(self.ui_R, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(UCSprite)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 2, 1, 1)
        self.ui_G = QtGui.QLineEdit(UCSprite)
        self.ui_G.setObjectName("ui_G")
        self.gridLayout.addWidget(self.ui_G, 0, 3, 1, 1)
        self.label_3 = QtGui.QLabel(UCSprite)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 4, 1, 1)
        self.ui_B = QtGui.QLineEdit(UCSprite)
        self.ui_B.setObjectName("ui_B")
        self.gridLayout.addWidget(self.ui_B, 0, 5, 1, 1)
        self.label_4 = QtGui.QLabel(UCSprite)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 6, 1, 1)
        self.ui_A = QtGui.QLineEdit(UCSprite)
        self.ui_A.setObjectName("ui_A")
        self.gridLayout.addWidget(self.ui_A, 0, 7, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtGui.QSpacerItem(20, 125, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(UCSprite)
        QtCore.QMetaObject.connectSlotsByName(UCSprite)

    def retranslateUi(self, UCSprite):
        UCSprite.setWindowTitle(QtGui.QApplication.translate("UCSprite", "Sprite", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("UCSprite", "경로", None, QtGui.QApplication.UnicodeUTF8))
        self.ui_find.setText(QtGui.QApplication.translate("UCSprite", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("UCSprite", "R", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("UCSprite", "G", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("UCSprite", "B", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("UCSprite", "A", None, QtGui.QApplication.UnicodeUTF8))

