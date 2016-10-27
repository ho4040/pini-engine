# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Dev\DevTool\User\Desinger-ui\LayerFrame.ui'
#
# Created: Thu Jul 17 15:51:13 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_LayerFrame(object):
    def setupUi(self, LayerFrame):
        LayerFrame.setObjectName("LayerFrame")
        LayerFrame.resize(206, 52)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(LayerFrame.sizePolicy().hasHeightForWidth())
        LayerFrame.setSizePolicy(sizePolicy)
        LayerFrame.setMaximumSize(QtCore.QSize(1000, 52))
        LayerFrame.setFrameShape(QtGui.QFrame.Box)
        LayerFrame.setFrameShadow(QtGui.QFrame.Sunken)
        LayerFrame.setLineWidth(2)
        LayerFrame.setMidLineWidth(1)
        self.layoutWidget = QtGui.QWidget(LayerFrame)
        self.layoutWidget.setGeometry(QtCore.QRect(7, 5, 191, 46))
        self.layoutWidget.setObjectName("layoutWidget")
        self.ui_layerFrameLayout = QtGui.QGridLayout(self.layoutWidget)
        self.ui_layerFrameLayout.setContentsMargins(2, 2, 2, 2)
        self.ui_layerFrameLayout.setContentsMargins(0, 0, 0, 0)
        self.ui_layerFrameLayout.setObjectName("ui_layerFrameLayout")
        self.ui_isVisible = QtGui.QCheckBox(self.layoutWidget)
        self.ui_isVisible.setChecked(True)
        self.ui_isVisible.setObjectName("ui_isVisible")
        self.ui_layerFrameLayout.addWidget(self.ui_isVisible, 1, 0, 1, 2)
        self.ui_isLock = QtGui.QCheckBox(self.layoutWidget)
        self.ui_isLock.setObjectName("ui_isLock")
        self.ui_layerFrameLayout.addWidget(self.ui_isLock, 1, 2, 1, 1)
        self.ui_nameInput = QtGui.QLineEdit(self.layoutWidget)
        self.ui_nameInput.setObjectName("ui_nameInput")
        self.ui_layerFrameLayout.addWidget(self.ui_nameInput, 0, 1, 1, 2)
        self.ui_nameLabel = QtGui.QLabel(self.layoutWidget)
        self.ui_nameLabel.setObjectName("ui_nameLabel")
        self.ui_layerFrameLayout.addWidget(self.ui_nameLabel, 0, 0, 1, 1)

        self.retranslateUi(LayerFrame)
        QtCore.QMetaObject.connectSlotsByName(LayerFrame)

    def retranslateUi(self, LayerFrame):
        LayerFrame.setWindowTitle(QtGui.QApplication.translate("LayerFrame", "Frame", None, QtGui.QApplication.UnicodeUTF8))
        self.ui_isVisible.setText(QtGui.QApplication.translate("LayerFrame", "isVisible", None, QtGui.QApplication.UnicodeUTF8))
        self.ui_isLock.setText(QtGui.QApplication.translate("LayerFrame", "isLock", None, QtGui.QApplication.UnicodeUTF8))
        self.ui_nameLabel.setText(QtGui.QApplication.translate("LayerFrame", "name", None, QtGui.QApplication.UnicodeUTF8))

