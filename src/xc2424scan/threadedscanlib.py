# -*- coding: utf-8 -*-

#    This file is part of the xc2424scan package
#    Copyright (C) 2005-2007 Mathieu Bouchard <mbouchar@bioinfo.ulaval.ca>
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
This is the Qt and threaded version of the scanlib library. Please note that you
can only call one threaded method at a time because of Qt limitations, socket
communications and design.
"""

__all__ = ["ThreadedXeroxC2424"]

from PyQt4.QtCore import QString, QThread, SIGNAL

from xc2424scan.scanlib import *

# @todo: Envoyer les résultats dans les signaux (ceux qui ne sont pas encore faits)
class ThreadedXeroxC2424(QThread):
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

    def __startMethod_(self, method, params = None):
        if self.isRunning():
            print "WARNING: Thread still running, waiting"
            self.wait()

        self.__method_ = method
        self.__params_ = params
        
        self.start()

    #
    # Get the folder list
    #
    def __getFolders_(self):
        self.folders = self.__scanner_.getFolders()
        self.emit(SIGNAL("foldersList()"))

    def getFolders(self):
        self.__startMethod_(self.__getFolders_)
        
    #
    # Get the files list
    #
    def __getFilesList_(self):
        self.files = self.__scanner_.getFilesList()
        self.emit(SIGNAL("filesList()"))
    
    def getFilesList(self):
        self.__startMethod_(self.__getFilesList_)
    
    #
    # Get the name of the current folder
    #
    def __getCurrentFolder_(self):
        folder = self.__scanner_.getCurrentFolder()
        self.emit(SIGNAL("currentFolder(const QString&)"), folder)
    
    def getCurrentFolder(self):
        self.__startMethod_(self.__getCurrentFolder_)
    
    #
    # Set the current folder
    #
    def __setFolder_(self):
        folder, password = self.__params_
        try:
            self.__scanner_.setFolder(folder, password)
            self.emit(SIGNAL("folderSet(const QString&)"), folder)
        except ProtectedError:
            self.emit(SIGNAL("folderProtected(const QString&)"), folder)
    
    def setFolder(self, folder, password = None):
        self.__startMethod_(self.__setFolder_, params = [folder, password])
    
    #
    # Get a file from the scanner
    #
    def __newPageHook_(self, current_page, file_size):
        self.emit(SIGNAL("newPage(int, int)"),
                  current_page, file_size)
    
    def __progressHook_(self, received_size):
        self.emit(SIGNAL("progress(int)"), received_size)
    
    def __getFile_(self):
        self.__scanner_.getFile(self.__params_["filename"],
                                self.__params_["save_filename"],
                                pages = self.__params_["pages"],
                                format = self.__params_["format"],
                                dpi = self.__params_["dpi"],
                                samplesize = self.__params_["samplesize"],
                                newpage_hook = self.__newPageHook_,
                                progress_hook = self.__progressHook_)
        self.emit(SIGNAL("fileReceived(const QString&)"),
                  self.__params_["filename"])
    
    def getFile(self, filename, save_filename, pages = None, 
                format = XeroxC2424.FORMAT_TIFF, dpi = [100, 100], 
                samplesize = 24):
        self.__startMethod_(self.__getFile_,
                            {"filename": filename,
                             "save_filename": save_filename,
                             "pages": pages,
                             "format": format,
                             "dpi": dpi,
                             "samplesize": samplesize})
    
    #
    # Get the preview of a file
    #
    def __getPreviews_(self):
        # Possible de faire un cache ici
        for filename in self.__params_:
            self.previews[filename] = self.__scanner_.getPreview(filename)
            self.emit(SIGNAL("previewReceived(const QString&)"), QString(filename))
        self.emit(SIGNAL("allPreviewReceived()"))

    def getPreviews(self, filenames):
        self.__startMethod_(self.__getPreviews_, params = filenames)
    
    #
    # Delete a file from the scanner
    #
    def __deleteFile_(self):
        self.__scanner_.deleteFile(self.__params_)
        self.emit(SIGNAL("fileDeleted(const QString&)"), self.__params_)
    
    def deleteFile(self, filename):
        self.__startMethod_(self.__deleteFile_, params = filename)
        
    #
    # Connect to the scanner
    #
    def __connectToScanner_(self):
        host, port = self.__params_
        self.__scanner_.connect(host, port)
        self.emit(SIGNAL("connectedToScanner()"))
        
    def connectToScanner(self, host, port):
        self.__startMethod_(self.__connectToScanner_, params = [host, port])

    @property
    def connected(self):
        return self.__scanner_.connected

    def run(self):
        try:
            self.__method_()
        except Exception, e:
            self.emit(SIGNAL("scanlibError(const QString&)"), str(e))

        self.__method_ = None
        self.__params_ = None
