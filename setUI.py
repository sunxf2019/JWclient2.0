# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'setUI.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog_Set(object):
    def setupUi(self, Dialog_Set):
        Dialog_Set.setObjectName("Dialog_Set")
        Dialog_Set.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog_Set.resize(600, 400)
        Dialog_Set.setMinimumSize(QtCore.QSize(600, 400))
        Dialog_Set.setMaximumSize(QtCore.QSize(600, 400))
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog_Set)
        self.buttonBox.setGeometry(QtCore.QRect(80, 360, 301, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.textEdit_set = QtWidgets.QTextEdit(Dialog_Set)
        self.textEdit_set.setGeometry(QtCore.QRect(10, 10, 581, 341))
        self.textEdit_set.setObjectName("textEdit_set")

        self.retranslateUi(Dialog_Set)
        self.buttonBox.accepted.connect(Dialog_Set.accept)
        self.buttonBox.rejected.connect(Dialog_Set.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog_Set)

    def retranslateUi(self, Dialog_Set):
        _translate = QtCore.QCoreApplication.translate
        Dialog_Set.setWindowTitle(_translate("Dialog_Set", "系统设置"))

