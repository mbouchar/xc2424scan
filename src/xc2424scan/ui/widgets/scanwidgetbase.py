# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'scanwidgetbase.ui'
#
# Created: Tue Apr 11 15:00:20 2006
#      by: PyQt4 UI code generator vsnapshot-20060129
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_ScanWidgetBase(object):
    def setupUi(self, ScanWidgetBase):
        ScanWidgetBase.setObjectName("ScanWidgetBase")
        ScanWidgetBase.resize(QtCore.QSize(QtCore.QRect(0,0,533,369).size()).expandedTo(ScanWidgetBase.minimumSizeHint()))
        
        self.hboxlayout = QtGui.QHBoxLayout(ScanWidgetBase)
        self.hboxlayout.setMargin(9)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")
        
        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.setMargin(0)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")
        
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setObjectName("hboxlayout1")
        
        self.label_8 = QtGui.QLabel(ScanWidgetBase)
        self.label_8.setObjectName("label_8")
        self.hboxlayout1.addWidget(self.label_8)
        
        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem)
        
        self.folder = QtGui.QComboBox(ScanWidgetBase)
        self.folder.setObjectName("folder")
        self.hboxlayout1.addWidget(self.folder)
        self.vboxlayout.addLayout(self.hboxlayout1)
        
        self.imageList = QtGui.QListWidget(ScanWidgetBase)
        self.imageList.setViewMode(QtGui.QListView.IconMode)
        self.imageList.setIconSize(QtCore.QSize(140,180))
        self.imageList.setMovement(QtGui.QListView.Static)
        self.imageList.setWrapping(True)
        self.imageList.setResizeMode(QtGui.QListView.Adjust)
        self.imageList.setSpacing(12)
        self.imageList.setObjectName("imageList")
        self.vboxlayout.addWidget(self.imageList)
        
        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setMargin(0)
        self.hboxlayout2.setSpacing(6)
        self.hboxlayout2.setObjectName("hboxlayout2")
        
        self.refresh = QtGui.QPushButton(ScanWidgetBase)
        self.refresh.setEnabled(False)
        self.refresh.setObjectName("refresh")
        self.hboxlayout2.addWidget(self.refresh)
        
        spacerItem1 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem1)
        self.vboxlayout.addLayout(self.hboxlayout2)
        self.hboxlayout.addLayout(self.vboxlayout)
        
        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setMargin(0)
        self.vboxlayout1.setSpacing(6)
        self.vboxlayout1.setObjectName("vboxlayout1")
        
        self.informations = QtGui.QGroupBox(ScanWidgetBase)
        self.informations.setObjectName("informations")
        
        self.gridlayout = QtGui.QGridLayout(self.informations)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")
        
        self.label_5 = QtGui.QLabel(self.informations)
        self.label_5.setObjectName("label_5")
        self.gridlayout.addWidget(self.label_5,0,0,1,1)
        
        self.info_nbPages = QtGui.QLabel(self.informations)
        self.info_nbPages.setObjectName("info_nbPages")
        self.gridlayout.addWidget(self.info_nbPages,0,1,1,1)
        
        self.label_6 = QtGui.QLabel(self.informations)
        self.label_6.setObjectName("label_6")
        self.gridlayout.addWidget(self.label_6,1,0,1,1)
        
        self.info_dpi = QtGui.QLabel(self.informations)
        self.info_dpi.setObjectName("info_dpi")
        self.gridlayout.addWidget(self.info_dpi,1,1,1,1)
        
        self.label_7 = QtGui.QLabel(self.informations)
        self.label_7.setObjectName("label_7")
        self.gridlayout.addWidget(self.label_7,2,0,1,1)
        
        self.info_resolution = QtGui.QLabel(self.informations)
        self.info_resolution.setObjectName("info_resolution")
        self.gridlayout.addWidget(self.info_resolution,2,1,1,1)
        self.vboxlayout1.addWidget(self.informations)
        
        self.options = QtGui.QGroupBox(ScanWidgetBase)
        self.options.setObjectName("options")
        
        self.gridlayout1 = QtGui.QGridLayout(self.options)
        self.gridlayout1.setMargin(9)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")
        
        self.delete = QtGui.QPushButton(self.options)
        self.delete.setEnabled(False)
        self.delete.setObjectName("delete")
        self.gridlayout1.addWidget(self.delete,6,1,1,1)
        
        self.color = QtGui.QComboBox(self.options)
        self.color.setEnabled(False)
        self.color.setObjectName("color")
        self.gridlayout1.addWidget(self.color,3,1,1,1)
        
        self.label = QtGui.QLabel(self.options)
        self.label.setObjectName("label")
        self.gridlayout1.addWidget(self.label,3,0,1,1)
        
        self.page = QtGui.QComboBox(self.options)
        self.page.setEnabled(False)
        self.page.setObjectName("page")
        self.gridlayout1.addWidget(self.page,1,1,1,1)
        
        self.label_4 = QtGui.QLabel(self.options)
        self.label_4.setObjectName("label_4")
        self.gridlayout1.addWidget(self.label_4,1,0,1,1)
        
        self.resolution = QtGui.QComboBox(self.options)
        self.resolution.setEnabled(False)
        self.resolution.setObjectName("resolution")
        self.gridlayout1.addWidget(self.resolution,2,1,1,1)
        
        self.label_2 = QtGui.QLabel(self.options)
        self.label_2.setObjectName("label_2")
        self.gridlayout1.addWidget(self.label_2,2,0,1,1)
        
        self.format = QtGui.QComboBox(self.options)
        self.format.setEnabled(False)
        self.format.setObjectName("format")
        self.gridlayout1.addWidget(self.format,0,1,1,1)
        
        self.label_3 = QtGui.QLabel(self.options)
        self.label_3.setObjectName("label_3")
        self.gridlayout1.addWidget(self.label_3,0,0,1,1)
        
        self.save = QtGui.QPushButton(self.options)
        self.save.setEnabled(False)
        self.save.setObjectName("save")
        self.gridlayout1.addWidget(self.save,5,1,1,1)
        
        spacerItem2 = QtGui.QSpacerItem(93,31,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout1.addItem(spacerItem2,4,1,1,1)
        self.vboxlayout1.addWidget(self.options)
        self.hboxlayout.addLayout(self.vboxlayout1)
        self.label.setBuddy(self.color)
        self.label_4.setBuddy(self.page)
        self.label_2.setBuddy(self.resolution)
        self.label_3.setBuddy(self.format)
        
        self.retranslateUi(ScanWidgetBase)
        QtCore.QMetaObject.connectSlotsByName(ScanWidgetBase)
    
    def tr(self, string):
        return QtGui.QApplication.translate("ScanWidgetBase", string, None, QtGui.QApplication.UnicodeUTF8)
    
    def retranslateUi(self, ScanWidgetBase):
        ScanWidgetBase.setWindowTitle(self.tr("Form"))
        self.label_8.setText(self.tr("Current Folder :"))
        self.refresh.setText(self.tr("&Refresh"))
        self.informations.setTitle(self.tr("File informations"))
        self.label_5.setText(self.tr("Number of pages :"))
        self.label_6.setText(self.tr("Scanned resolution :"))
        self.label_7.setText(self.tr("Image size :"))
        self.options.setTitle(self.tr("Options"))
        self.delete.setText(self.tr("&Delete"))
        self.label.setText(self.tr("Color"))
        self.label_4.setText(self.tr("Page"))
        self.label_2.setText(self.tr("Resolution"))
        self.format.addItem(self.tr("tiff"))
        self.format.addItem(self.tr("gif"))
        self.format.addItem(self.tr("jpeg"))
        self.format.addItem(self.tr("bmp"))
        self.format.addItem(self.tr("pdf"))
        self.label_3.setText(self.tr("Format"))
        self.save.setText(self.tr("&Save"))
