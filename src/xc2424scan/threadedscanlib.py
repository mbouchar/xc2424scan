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
@author: Mathieu Bouchard
@version: 0.1
"""

__all__ = ["ThreadedXeroxC2424"]

from PyQt4.QtCore import QString, QThread, SIGNAL

from xc2424scan.scanlib import XeroxC2424, ProtectedError

class ThreadedXeroxC2424(QThread):
    """@todo: Créer un mutex pour qu'une seule fonction soit exécutée à la fois
    """
    
    def __init__(self, debug = False):
        """
        """
        QThread.__init__(self)
        
        # The lib used to connect to the scanner
        self.__scanner_ = XeroxC2424(debug)
        self.__method_ = None
        self.__params_ = None
        
        self.files = None
        self.folders = None
        self.previews = {}
        
    #
    # Gets the folder list
    #
    def __getFolders_(self):
        self.folders = self.__scanner_.getFolders()
        self.emit(SIGNAL("foldersList()"))

    def getFolders(self):
        self.__method_ = self.__getFolders_
        self.start()
        
    #
    # Gets the files list
    #
    def __getFiles_(self):
        self.files = self.__scanner_.getFiles()
        self.emit(SIGNAL("filesList()"))
    
    def getFiles(self):
        self.__method_ = self.__getFiles_
        self.start()
    
    #
    # Gets the name of the current folder
    #
    def __getCurrentFolder_(self):
        folder = self.__scanner_.getCurrentFolder()
        self.emit(SIGNAL("currentFolder(const QString&)"), folder)
    
    def getCurrentFolder(self):
        self.__method_ = self.__getCurrentFolder_
        self.start()
    
    #
    # Sets the current folder
    #
    def __setFolder_(self):
        folder, password = self.__params_
        try:
            self.__scanner_.setFolder(folder, password)
            self.emit(SIGNAL("folderSet(const QString&)"), folder)
        except ProtectedError:
            self.emit(SIGNAL("folderProtected(const QString&)"), folder)
    
    def setFolder(self, folder, password = None):
        self.__method_ = self.__setFolder_
        self.__params_ = [folder, password]
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
        self.emit(SIGNAL("fileReceived(const QString&)"),
                  self.__params_["filename"])
    
    def getFile(self, filename, save_filename, page = None, 
                format = XeroxC2424.FORMAT_TIFF, dpi = [100, 100], 
                samplesize = 24):
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
    def __getPreviews_(self):
        # Possible de faire un cache ici
        for filename in self.__params_:
            self.previews[filename] = self.__scanner_.getPreview(filename)
            self.emit(SIGNAL("previewReceived(const QString&)"), QString(filename))
    
    def getPreviews(self, filenames):
        self.__method_ = self.__getPreviews_
        self.__params_ = filenames
        self.start()
    
    #
    # Delete a file from the scanner
    #
    def __deleteFile_(self):
        self.__scanner_.deleteFile(self.__params_)
        self.emit(SIGNAL("fileDeleted(const QString&)"), self.__params_)
    
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
