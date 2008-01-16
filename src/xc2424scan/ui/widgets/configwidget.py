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

__all__ = ["ConfigWidget"]

from PyQt4.QtCore import SIGNAL, Qt
from PyQt4.QtGui import QWidget
from xc2424scan.ui.widgets.configwidgetbase import Ui_ConfigWidgetBase
from xc2424scan.config import Config

class ConfigWidget(QWidget, object):
    """This is the config widget for the xc2424scan software. Actually, it is
    only used to set the scanner ip and port.
    """

    def __init__(self, parent = None):
        """Create a new config widget
        
        @param parent: The parent widget
        @type parent: QWidget
        """
        QWidget.__init__(self, parent)
        self.__basewidget_ = Ui_ConfigWidgetBase()
        self.__basewidget_.setupUi(self)
        
        # Redirect to the base widget buttons to connect slots in parent
        self.ok = self.__basewidget_.ok
        self.cancel = self.__basewidget_.cancel

        # Config reset button        
        self.connect(self.__basewidget_.useDefault, SIGNAL("clicked(bool)"),
                        self.__ui_useDefault_clicked_)

    def __ui_useDefault_clicked_(self, clicked):
        if clicked:
           self.__basewidget_.scannerPort.setValue(Config.DEFAULT_PORT)
        self.__basewidget_.scannerPort.setEnabled(not clicked)
        
    def getAddress(self):
        return str(self.__basewidget_.scannerAddress.text())
    
    def setAddress(self, address):
        if isinstance(address, str):
            self.__basewidget_.scannerAddress.setText(address)
        else:
            self.__basewidget_.scannerAddress.setText("")

    def getPort(self):
        return self.__basewidget_.scannerPort.value()
    
    def setPort(self, port):
        self.__basewidget_.scannerPort.setValue(port)
        if port != Config.DEFAULT_PORT:
            self.__basewidget_.useDefault.setCheckState(Qt.Unchecked)
            self.__basewidget_.scannerPort.setEnabled(True)
        else:
            self.__basewidget_.useDefault.setCheckState(Qt.Checked)
            self.__basewidget_.scannerPort.setEnabled(False)
