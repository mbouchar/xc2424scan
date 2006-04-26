# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'configwidgetbase.ui'
#
# Created: Tue Feb  7 15:56:10 2006
#      by: PyQt4 UI code generator vsnapshot-20060129
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_ConfigWidgetBase(object):
    def setupUi(self, ConfigWidgetBase):
        ConfigWidgetBase.setObjectName("ConfigWidgetBase")
        ConfigWidgetBase.resize(QtCore.QSize(QtCore.QRect(0,0,361,174).size()).expandedTo(ConfigWidgetBase.minimumSizeHint()))
        
        self.vboxlayout = QtGui.QVBoxLayout(ConfigWidgetBase)
        self.vboxlayout.setMargin(9)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")
        
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
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
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setObjectName("hboxlayout1")
        
        self.useDefault = QtGui.QCheckBox(ConfigWidgetBase)
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
        self.hboxlayout2.setMargin(0)
        self.hboxlayout2.setSpacing(6)
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
    
    def tr(self, string):
        return QtGui.QApplication.translate("ConfigWidgetBase", string, None, QtGui.QApplication.UnicodeUTF8)
    
    def retranslateUi(self, ConfigWidgetBase):
        ConfigWidgetBase.setWindowTitle(self.tr("Form"))
        self.label.setText(self.tr("Scanner address :"))
        self.useDefault.setText(self.tr("Do not use default port"))
        self.ok.setText(self.tr("Ok"))
        self.cancel.setText(self.tr("Cancel"))
