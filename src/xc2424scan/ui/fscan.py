# -*- coding: utf-8 -*-

#    This file is part of the xc2424scan package
#    Copyright (C) 2005-2008 Mathieu Bouchard <mbouchar@bioinfo.ulaval.ca>
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
These are the main dialogs for the xc2424scan software
"""

__all__ = ["FScan"]

import sys

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QMainWindow, QDialog, QVBoxLayout, QMenuBar, QMenu, \
                        QAction, QStatusBar

from xc2424scan.ui.widgets.scanwidget import ScanWidget
from xc2424scan.ui.widgets.configwidget import ConfigWidget
from xc2424scan.config import Config
from xc2424scan import version

class FScanConfig(QDialog):
    """Configuration dialog"""
    
    def __init__(self, parent):
        """Create a new configuration dialog
        
        @param parent: Parent widget
        @type parent: QWidget
        """
        QDialog.__init__(self, parent)
        self.setWindowTitle(_("Configuration"))

        # Set the main config widget
        self.config = ConfigWidget(self)
        self.__layout_ = QVBoxLayout(self)
        self.__layout_.setMargin(0)
        self.__layout_.setSpacing(0)
        self.__layout_.addWidget(self.config)
        
        self.connect(self.config.ok, SIGNAL("clicked()"), self.__ui_ok_clicked_)
        self.connect(self.config.cancel, SIGNAL("clicked()"),
                     self.__ui_cancel_clicked_)
    
    def __ui_ok_clicked_(self):
        """This is called when the user click on the OK button"""
        self.accept()
        
    def __ui_cancel_clicked_(self):
        """This is called when the user click on the Cancel button or close the
        dialog"""
        self.reject()
        
class FScan(QMainWindow):
    """This is the main windown of the xc2424scan software"""
    
    def __init__(self, parent = None):
        """Create a new main window
        
        @param parent: Parent widget
        @type parent: QWidget
        """
        QMainWindow.__init__(self, parent)
        self.setWindowTitle(_("Xerox WorkCentre C2424 Scanner Utility v%s") %
                            version.__version__)
        
        # Get the software configuration (~/.xc2424scan) or show the config
        # dialog if there is no configuration file
        self.__config_ = Config()
        if self.__config_.address is None:
            if self.__show_config_() is False:
                sys.exit()
            self.__config_.reload()

        # Set the main widget        
        self.__scanWidget_ = ScanWidget(self, self.__config_.debug)
        self.setCentralWidget(self.__scanWidget_)
        
        self.__scanWidget_.connectToScanner(self.__config_.address, 
                                            self.__config_.port)

        # Create the menu
        self.__setupMenu_()

    def __setupMenu_(self):
        """Used to create the default menu"""
        # Create the menu bar
        self.__menu_ = QMenuBar(self)
        self.setMenuBar(self.__menu_)
        
        # File
        self.menuFile = QMenu(self.__menu_)
        self.actionQuit   = QAction(self)
        self.menuFile.setTitle(_("&File"))
        self.menuFile.addAction(self.actionQuit)
        self.actionQuit.setText(_("&Quit"))

        # Settings
        self.menuSettings    = QMenu(self.__menu_)
        self.actionConfigure = QAction(self)
        self.menuSettings.addAction(self.actionConfigure)
        self.menuSettings.setTitle(_("&Settings"))
        self.actionConfigure.setText(_("&Configure xc2424scan"))

        # Add the menus to the menu
        self.__menu_.addAction(self.menuFile.menuAction())
        self.__menu_.addAction(self.menuSettings.menuAction())
        
        self.connect(self.actionQuit, SIGNAL("triggered(bool)"), 
                     self.close)
        self.connect(self.actionConfigure, SIGNAL("triggered(bool)"),
                     self.__change_config_)

    def __change_config_(self):
        """Called when the configuration has changed and we need to reconnect
        to the scanner"""
        if self.__show_config_():
            self.__scanWidget_.connectToScanner(self.__config_.address, 
                                                self.__config_.port)

    def __show_config_(self):
        """Called when we need to show the config dialog
        
        @return: True if the config has changed, False otherwise
        @rtype: bool
        """
        fconfig = FScanConfig(self)
        fconfig.config.setAddress(self.__config_.address)
        fconfig.config.setPort(self.__config_.port)
        
        if fconfig.exec_() == QDialog.Accepted:
            self.__config_.address = fconfig.config.getAddress()
            self.__config_.port = fconfig.config.getPort()
            return True
        else:
            return False
