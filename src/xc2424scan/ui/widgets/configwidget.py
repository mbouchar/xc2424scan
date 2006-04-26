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
This is the main widget of the xc2424scan application
This widget is self contained and can be included in any other Qt4
application.

@author: Mathieu Bouchard
@version: 0.1
"""

__all__ = ["ConfigWidget"]

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QWidget
from xc2424scan.ui.widgets.configwidgetbase import Ui_ConfigWidgetBase
from xc2424scan.config import Config

class ConfigWidget(QWidget, object):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.__basewidget_ = Ui_ConfigWidgetBase()
        self.__basewidget_.setupUi(self)
        
        # @todo: redirection temporaire
        self.ok = self.__basewidget_.ok
        self.cancel = self.__basewidget_.cancel
        
        self.connect(self.__basewidget_.useDefault, SIGNAL("clicked(bool)"),
                        self.__useDefault_clicked_)

    def __useDefault_clicked_(self, clicked):
        self.__basewidget_.scannerPort.setEnabled(clicked)
        
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
