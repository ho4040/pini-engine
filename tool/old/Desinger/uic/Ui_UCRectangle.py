# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/choiyoung/Desktop/works/DevTool/User/Desinger-ui/UCRectangle.ui'
#
# Created: Thu Jul 17 12:31:20 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_UCRectangle(object):
    def setupUi(self, UCRectangle):
        UCRectangle.setObjectName("UCRectangle")
        UCRectangle.resize(357, 161)
        self.verticalLayout = QtGui.QVBoxLayout(UCRectangle)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(UCRectangle)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.ui_R = QtGui.QLineEdit(UCRectangle)
        self.ui_R.setObjectName("ui_R")
        self.gridLayout.addWidget(self.ui_R, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(UCRectangle)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 2, 1, 1)
        self.ui_G = QtGui.QLineEdit(UCRectangle)
        self.ui_G.setObjectName("ui_G")
        self.gridLayout.addWidget(self.ui_G, 0, 3, 1, 1)
        self.label_3 = QtGui.QLabel(UCRectangle)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 4, 1, 1)
        self.ui_B = QtGui.QLineEdit(UCRectangle)
        self.ui_B.setObjectName("ui_B")
        self.gridLayout.addWidget(self.ui_B, 0, 5, 1, 1)
        self.label_4 = QtGui.QLabel(UCRectangle)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 6, 1, 1)
        self.ui_A = QtGui.QLineEdit(UCRectangle)
        self.ui_A.setObjectName("ui_A")
        self.gridLayout.addWidget(self.ui_A, 0, 7, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtGui.QSpacerItem(20, 125, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(UCRectangle)
        QtCore.QMetaObject.connectSlotsByName(UCRectangle)

    def retranslateUi(self, UCRectangle):
        UCRectangle.setWindowTitle(QtGui.QApplication.translate("UCRectangle", "Rectangle", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("UCRectangle", "R", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("UCRectangle", "G", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("UCRectangle", "B", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("UCRectangle", "A", None, QtGui.QApplication.UnicodeUTF8))

