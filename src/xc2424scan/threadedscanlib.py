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
This library is able to communicate with the Xerox WorkCentre C2424
scanning protocol used by the binary windows application Xerox Scan Utility
used to retrieve the scanned images from the printer.

The library offers only some high-level functions. To have more informations
about the protocol used by the Xerox Scan Utility, please read the file
protocol.txt

@author: Mathieu Bouchard
@version: 0.1
"""

__all__ = ["ThreadedXeroxC2424"]

from PyQt4.QtCore import QThread

from xc2424scan.scanlib import XeroxC2424

class ThreadedXeroxC2424(QThread):
    """@todo: Créer un mutex pour qu'une seule fonction soit exécutée à la fois
    """
    
    def __init__(self):
        """
        """
        QThread.__init__(self)
        
        # The lib used to connect to the scanner
        self.__scanner_ = XeroxC2424()
        self.__method_ = None
        self.__params_ = None
        
    #
    # Gets the folder list
    #
    def __getFolders_(self):
        folders = self.__scanner_.getFolders()
        self.emit(SIGNAL("foldersList"), folders)

    def getFolders(self):
        self.__method_ = self.__refreshFoldersList_
        self.start()
        
    #
    # Gets the files list
    #
    def __getFiles_(self):
        files = self.__scanner_.getFiles()
        self.emit(SIGNAL("filesList"), files)
    
    def getFiles(self):
        self.__method_ = self.__getFiles_
        self.start()
    
    #
    # Gets the name of the current folder
    #
    def __getCurrentFolder_(self):
        folder = self.__scanner_.getCurrentFolder()
        self.emit(SIGNAL("currentFolder"), folder)
    
    def getCurrentFolder(self):
        self.__method_ = self.__getCurrentFolder_
        self.start()
    
    #
    # Sets the current folder
    #
    def __setFolder_(self):
        self.__scanner_.setFolder(self.__params_)
        self.emit(SIGNAL("folderSet"))
    
    def setFolder(self, folder):
        self.__method_ = self.__setFolder_
        self.__params_ = folder
        self.start()
    
    #
    # Gets a file from the scanner
    #
    def __getFile_(self):
        self.__scanner_.getFile(self.__params_["filename"],
                                self.__params_["save_filename"],
                                self.__params_["page"],
                                self.__params_["format"],
                                self.__params_["dpi"],
                                self.__params_["samplesize"])
        self.emit(SIGNAL("fileReceived"), self.__params_["filename"])
    
    def getFile(self, filename, save_filename, page = None, 
                format = FORMAT_TIFF, dpi = [100, 100], samplesize = 24):
        self.__method_ = self.__getFile_
        self.__params_ = {"filename": filename,
                          "save_filename": save_filename,
                          "page": page,
                          "format": format,
                          "dpi": dpi,
                          "samplesize": samplesize}
        self.start()
    
    #
    # Gets the preview of a file
    #
    def __getPreview_(self):
        data = self.__scanner_.getPreview(self.__params_)
        self.emit(SIGNAL("previewReceived"), self.__params_, data)
    
    def getPreview(self, filename):
        self.__method_ = self.__getPreview_
        self.__params_ = filename
        self.start()
    
    #
    # Delete a file from the scanner
    #
    def __deleteFile_(self):
        self.__scanner_.deleteFile(self.__params_)
        self.emit(SIGNAL("fileDeleted"), self.__params_)
    
    def deleteFile(self, filename):
        self.__method_ = self.__deleteFile_
        self.__params_ = filename
        self.start()
        
    #
    # Connect to the scanner
    #
    def __connectToScanner_(self):
        self.__scanner_.connect(self.__host_, self.__port_)
        self.emit(SIGNAL("connectedToScanner()"))
        
    def connectToScanner(self, host, port):
        self.__method_ = self.__connectToScanner_
        self.__host_ = host
        self.__port_ = port
        self.start()

    def run(self):
        # @todo: Créer un mutex
        self.__method_()
