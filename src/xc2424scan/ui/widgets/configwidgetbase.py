# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/xc2424scan/ui/widgets/configwidgetbase.ui'
#
# Created: Wed Jan 16 09:50:40 2008
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_ConfigWidgetBase(object):
    def setupUi(self, ConfigWidgetBase):
        ConfigWidgetBase.setObjectName("ConfigWidgetBase")
        ConfigWidgetBase.resize(QtCore.QSize(QtCore.QRect(0,0,361,174).size()).expandedTo(ConfigWidgetBase.minimumSizeHint()))

        self.vboxlayout = QtGui.QVBoxLayout(ConfigWidgetBase)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setMargin(9)
        self.vboxlayout.setObjectName("vboxlayout")

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName("hboxlayout")

        self.label = QtGui.QLabel(ConfigWidgetBase)
        self.label.setObjectName("label")
        self.hboxlayout.addWidget(self.label)

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)

        self.scannerAddress = QtGui.QLineEdit(ConfigWidgetBase)
        self.scannerAddress.setObjectName("scannerAddress")
        self.hboxlayout.addWidget(self.scannerAddress)
        self.vboxlayout.addLayout(self.hboxlayout)

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.useDefault = QtGui.QCheckBox(ConfigWidgetBase)
        self.useDefault.setChecked(True)
        self.useDefault.setObjectName("useDefault")
        self.hboxlayout1.addWidget(self.useDefault)

        spacerItem1 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem1)

        self.scannerPort = QtGui.QSpinBox(ConfigWidgetBase)
        self.scannerPort.setEnabled(False)
        self.scannerPort.setMaximum(65536)
        self.scannerPort.setObjectName("scannerPort")
        self.hboxlayout1.addWidget(self.scannerPort)
        self.vboxlayout.addLayout(self.hboxlayout1)

        spacerItem2 = QtGui.QSpacerItem(343,71,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout.addItem(spacerItem2)

        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setSpacing(6)
        self.hboxlayout2.setMargin(0)
        self.hboxlayout2.setObjectName("hboxlayout2")

        spacerItem3 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem3)

        self.ok = QtGui.QPushButton(ConfigWidgetBase)
        self.ok.setDefault(True)
        self.ok.setObjectName("ok")
        self.hboxlayout2.addWidget(self.ok)

        self.cancel = QtGui.QPushButton(ConfigWidgetBase)
        self.cancel.setObjectName("cancel")
        self.hboxlayout2.addWidget(self.cancel)
        self.vboxlayout.addLayout(self.hboxlayout2)
        self.label.setBuddy(self.scannerAddress)

        self.retranslateUi(ConfigWidgetBase)
        QtCore.QMetaObject.connectSlotsByName(ConfigWidgetBase)

    def retranslateUi(self, ConfigWidgetBase):
        ConfigWidgetBase.setWindowTitle(QtGui.QApplication.translate("ConfigWidgetBase", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ConfigWidgetBase", "Scanner address :", None, QtGui.QApplication.UnicodeUTF8))
        self.useDefault.setText(QtGui.QApplication.translate("ConfigWidgetBase", "Use default port", None, QtGui.QApplication.UnicodeUTF8))
        self.ok.setText(QtGui.QApplication.translate("ConfigWidgetBase", "Ok", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel.setText(QtGui.QApplication.translate("ConfigWidgetBase", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

