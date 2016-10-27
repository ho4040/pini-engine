# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/choiyoung/Desktop/works/DevTool/User/Desinger-ui/UCTransform.ui'
#
# Created: Thu Jul 17 12:31:21 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_UCTransform(object):
    def setupUi(self, UCTransform):
        UCTransform.setObjectName("UCTransform")
        UCTransform.resize(313, 102)
        self.verticalLayout = QtGui.QVBoxLayout(UCTransform)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSpacing(2)
        self.gridLayout.setObjectName("gridLayout")
        self.label_5 = QtGui.QLabel(UCTransform)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 1, 0, 1, 1)
        self.ui_X = QtGui.QLineEdit(UCTransform)
        self.ui_X.setObjectName("ui_X")
        self.gridLayout.addWidget(self.ui_X, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(UCTransform)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.label_3 = QtGui.QLabel(UCTransform)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)
        self.ui_Y = QtGui.QLineEdit(UCTransform)
        self.ui_Y.setObjectName("ui_Y")
        self.gridLayout.addWidget(self.ui_Y, 0, 3, 1, 2)
        self.ui_Width = QtGui.QLineEdit(UCTransform)
        self.ui_Width.setObjectName("ui_Width")
        self.gridLayout.addWidget(self.ui_Width, 1, 1, 1, 1)
        self.label_6 = QtGui.QLabel(UCTransform)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 1, 2, 1, 1)
        self.ui_Height = QtGui.QLineEdit(UCTransform)
        self.ui_Height.setObjectName("ui_Height")
        self.gridLayout.addWidget(self.ui_Height, 1, 3, 1, 2)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtGui.QSpacerItem(17, 30, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(UCTransform)
        QtCore.QMetaObject.connectSlotsByName(UCTransform)
        UCTransform.setTabOrder(self.ui_X, self.ui_Y)
        UCTransform.setTabOrder(self.ui_Y, self.ui_Width)
        UCTransform.setTabOrder(self.ui_Width, self.ui_Height)

    def retranslateUi(self, UCTransform):
        UCTransform.setWindowTitle(QtGui.QApplication.translate("UCTransform", "Transform", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("UCTransform", "Width", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("UCTransform", "X", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("UCTransform", "Y", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("UCTransform", "Height", None, QtGui.QApplication.UnicodeUTF8))

