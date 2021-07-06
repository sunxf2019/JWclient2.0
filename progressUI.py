# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'progressUI.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog_Progress(object):
    def setupUi(self, Dialog_Progress):
        Dialog_Progress.setObjectName("Dialog_Progress")
        Dialog_Progress.setWindowModality(QtCore.Qt.WindowModal)
        Dialog_Progress.setEnabled(False)
        Dialog_Progress.resize(380, 70)
        Dialog_Progress.setMinimumSize(QtCore.QSize(380, 70))
        Dialog_Progress.setMaximumSize(QtCore.QSize(380, 70))
        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog_Progress)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 361, 51))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_Progress = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("宋体")
        font.setPointSize(12)
        self.label_Progress.setFont(font)
        self.label_Progress.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_Progress.setText("")
        self.label_Progress.setObjectName("label_Progress")
        self.verticalLayout.addWidget(self.label_Progress)
        self.progressBar = QtWidgets.QProgressBar(self.verticalLayoutWidget)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)

        self.retranslateUi(Dialog_Progress)
        QtCore.QMetaObject.connectSlotsByName(Dialog_Progress)

    def retranslateUi(self, Dialog_Progress):
        _translate = QtCore.QCoreApplication.translate
        Dialog_Progress.setWindowTitle(_translate("Dialog_Progress", "Dialog"))

