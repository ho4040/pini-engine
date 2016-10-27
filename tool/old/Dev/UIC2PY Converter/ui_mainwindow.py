# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test.ui'
#
# Created: Tue Jul 01 14:47:39 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(281, 274)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setSpacing(3)
        self.verticalLayout_2.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.input = QtGui.QLineEdit(self.centralwidget)
        self.input.setObjectName("input")
        self.horizontalLayout.addWidget(self.input)
        self.input_find = QtGui.QPushButton(self.centralwidget)
        self.input_find.setMaximumSize(QtCore.QSize(50, 16777215))
        self.input_find.setObjectName("input_find")
        self.horizontalLayout.addWidget(self.input_find)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.output = QtGui.QLineEdit(self.centralwidget)
        self.output.setObjectName("output")
        self.horizontalLayout_2.addWidget(self.output)
        self.output_find = QtGui.QPushButton(self.centralwidget)
        self.output_find.setMaximumSize(QtCore.QSize(50, 16777215))
        self.output_find.setObjectName("output_find")
        self.horizontalLayout_2.addWidget(self.output_find)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.textEdit = QtGui.QTextEdit(self.centralwidget)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout.addWidget(self.textEdit)
        self.start = QtGui.QPushButton(self.centralwidget)
        self.start.setObjectName("start")
        self.verticalLayout.addWidget(self.start)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "입력 폴더", None, QtGui.QApplication.UnicodeUTF8))
        self.input_find.setText(QtGui.QApplication.translate("MainWindow", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "출력 폴더", None, QtGui.QApplication.UnicodeUTF8))
        self.output_find.setText(QtGui.QApplication.translate("MainWindow", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.start.setText(QtGui.QApplication.translate("MainWindow", "변환", None, QtGui.QApplication.UnicodeUTF8))

