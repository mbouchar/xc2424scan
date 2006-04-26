# -*- coding: utf-8 -*-

#    This file is part of the xc2424scan package
#    Copyright (C) 2005 Mathieu Bouchard <mbouchar@bioinfo.ulaval.ca>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
This is the main form of the xc2424scan application

@author: Mathieu Bouchard
@version: 0.1
"""

__all__ = ["FScan"]

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QMainWindow, QDialog, QVBoxLayout, QMenuBar, QMenu, \
                        QAction, QStatusBar
import sys

from xc2424scan.ui.widgets.scanwidget import ScanWidget
from xc2424scan.ui.widgets.configwidget import ConfigWidget
from xc2424scan.config import Config
from xc2424scan import version

class FScanConfig(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setWindowTitle("Configuration")
        
        self.config = ConfigWidget(self)
        self.__layout_ = QVBoxLayout(self)
        self.__layout_.setMargin(0)
        self.__layout_.setSpacing(0)
        self.__layout_.addWidget(self.config)
        
        self.connect(self.config.ok, SIGNAL("clicked()"), self.__ok_clicked_)
        self.connect(self.config.cancel, SIGNAL("clicked()"), self.__cancel_clicked_)
    
    def __ok_clicked_(self):
        self.accept()
        
    def __cancel_clicked_(self):
        self.reject()
        
class FScan(QMainWindow):
    def __init__(self, parent = None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle("Xerox WorkCentre C2424 Scanner Utility v%s" %
                            version.__version__)
        self.__scanWidget_ = ScanWidget(self)
        self.setCentralWidget(self.__scanWidget_)
        
        self.__config_ = Config()
        if self.__config_.address is None:
            if self.__show_config_() is False:
                sys.exit()
            self.__config_.reload()
        
        self.__scanWidget_.connectToScanner(self.__config_.address, 
                                            self.__config_.port)

        self.__setupMenu_()

        #self.__statusbar_ = QStatusBar(self)
        #self.setStatusBar(self.__statusbar_)

    def __setupMenu_(self):
        self.__menu_ = QMenuBar(self)
        self.setMenuBar(self.__menu_)
        
        # File
        self.menuFile = QMenu(self.__menu_)
        self.actionQuit   = QAction(self)
        self.menuFile.setTitle("&File")
        self.menuFile.addAction(self.actionQuit)
        self.actionQuit.setText("&Quit")

        # Settings
        self.menuSettings    = QMenu(self.__menu_)
        self.actionConfigure = QAction(self)
        self.menuSettings.addAction(self.actionConfigure)
        self.menuSettings.setTitle("&Settings")
        self.actionConfigure.setText("&Configure xc2424scan")

        self.__menu_.addAction(self.menuFile.menuAction())
        self.__menu_.addAction(self.menuSettings.menuAction())
        
        self.connect(self.actionQuit, SIGNAL("triggered(bool)"), 
                     self.close)
        self.connect(self.actionConfigure, SIGNAL("triggered(bool)"),
                     self.__change_config_)

    def __change_config_(self):
        if self.__show_config_():
            self.__scanWidget_.connectToScanner(self.__config_.address, 
                                                self.__config_.port)

    def __show_config_(self):
        fconfig = FScanConfig(self)
        fconfig.config.setAddress(self.__config_.address)
        fconfig.config.setPort(self.__config_.port)
        
        if fconfig.exec_() == QDialog.Accepted:
            self.__config_.address = fconfig.config.getAddress()
            self.__config_.port = fconfig.config.getPort()
            return True
        else:
            return False