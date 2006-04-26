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

__all__ = ["ScanWidget"]

from PyQt4.QtCore import QDir, QObject, QRect, Qt, SIGNAL
from PyQt4.QtGui import QWidget, QFileDialog, QListWidgetItem, QPixmap, \
                        QIcon, QMessageBox, QInputDialog, QLineEdit, QPainter
import os

from xc2424scan.scanlib import XeroxC2424, ProtectedError, SocketError, \
                               NoPreviewError
from xc2424scan.ui.widgets.scanwidgetbase import Ui_ScanWidgetBase

class ScanWidget(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.__basewidget_ = Ui_ScanWidgetBase()
        self.__basewidget_.setupUi(self)
        
        # The lib used to connect to the scanner
        self.__scanner_ = XeroxC2424()
        # List of files available on the scanner
        self.__scanned_files_ = None
        # Last folder visited (see __showFolder_)
        self.__last_folder_ = None
        
        QObject.connect(self.__basewidget_.refresh, SIGNAL("clicked()"),
                        self.__refreshFolder_)
        QObject.connect(self.__basewidget_.folder, SIGNAL("activated(const QString&)"),
                        self.__showFolder_)
        QObject.connect(self.__basewidget_.imageList, 
                        SIGNAL("currentTextChanged(const QString&)"),
                        self.__showFile_)
        QObject.connect(self.__basewidget_.delete, SIGNAL("clicked()"),
                        self.__deleteFile_)
        QObject.connect(self.__basewidget_.format, SIGNAL("currentIndexChanged(const QString&)"),
                        self.__setFormat_)
        QObject.connect(self.__basewidget_.save, SIGNAL("clicked()"),
                        self.__saveFile_)

    def connectToScanner(self, host, port):
        self.__scanner_.connect(host, port)
        # Affichage du répertoire public
        self.__refreshFolders_()
        self.__showFolder_("Public")
    
    def disconnect(self):
        self.__scanner_.disconnect()
    
    def __refreshFolders_(self):
        self.setEnabled(False)
        
        self.__basewidget_.folder.clear()
        for folder in self.__scanner_.getFolders():
            self.__basewidget_.folder.addItem(folder)
            
        self.setEnabled(True)
    
    def __refreshFolder_(self):
        # @todo: Il va y avoir pas mal plus de stock à mettre disabled
        self.__basewidget_.refresh.setEnabled(False)
        self.__basewidget_.delete.setEnabled(False)
        self.__basewidget_.imageList.clear()

        # Ajout des fichiers présents dans le répertoire
        self.__scanned_files_ = self.__scanner_.getFiles()
        painter = QPainter()
        painter.setPen(Qt.black);

        for filename in self.__scanned_files_.keys():
            # Récupération du preview de l'image
            pixmap = QPixmap()
            try:
                # @todo: Preview avec un filename non fixe
                preview = self.__scanner_.getPreview(filename)
                pixmap.loadFromData(preview)
                
                # creation of a black border
                painter.begin(pixmap)
                width = self.__scanned_files_[filename]["respreview"][0] - 1
                height = self.__scanned_files_[filename]["respreview"][1] - 1
                painter.drawRect(QRect(0, 0, width, height))
                painter.end()
            except NoPreviewError:
                # @todo: Le prefix peut changer
                pixmap.load("/usr/share/xc2424scan/nopreview.png")
            
            self.__basewidget_.imageList.addItem(QListWidgetItem(QIcon(pixmap), filename))
        self.__basewidget_.imageList.sortItems()
        
        self.__basewidget_.refresh.setEnabled(True)
        if self.__basewidget_.imageList.currentItem() != None:
            self.__basewidget_.delete.setEnabled(True)
    
    def __showFolder_(self, folder):
        folder = str(folder)
        try:
            self.__scanner_.setFolder(folder)
            self.__refreshFolder_()
        except ProtectedError:
            password, result = QInputDialog.getText(self, "Accessing a protected folder",
                                                    "Please enter the password for the protected " \
                                                    "folder %s" % folder, QLineEdit.Password)
 
            if result is True:
                try:
                    self.__scanner_.setFolder(folder, str(password))
                    self.__refreshFolder_()
                except (ValueError, ProtectedError):
                    QMessageBox.warning(self, "Invalid password", 
                                        "The password entered is not valid",
                                        QMessageBox.Ok, QMessageBox.NoButton)
                    self.__basewidget_.folder.setCurrentIndex(self.__last_folder_)
                    return
                
        self.__last_folder_ = self.__basewidget_.folder.currentIndex()

    def __showFile_(self, filename):
        filename = str(filename)
        
        if filename == "":
            self.__basewidget_.info_nbPages.setText("")
            self.__basewidget_.info_dpi.setText("")
            self.__basewidget_.info_resolution.setText("")
            
            self.__clearOptions_()
            
            self.__basewidget_.delete.setEnabled(False)
            self.__basewidget_.save.setEnabled(False)
            self.__basewidget_.format.setEnabled(False)
            self.__basewidget_.page.setEnabled(False)
            self.__basewidget_.resolution.setEnabled(False)
            self.__basewidget_.color.setEnabled(False)
        else:
            file_infos = self.__scanned_files_[filename]
            # Affichage des informations
            self.__basewidget_.info_nbPages.setText(str(file_infos["nbpages"]))
            self.__basewidget_.info_dpi.setText("%dx%d dpi" % (file_infos["dpi"][0], file_infos["dpi"][1]))
            self.__basewidget_.info_resolution.setText("%dx%d" % (file_infos["resolution"][0], file_infos["resolution"][1]))
            
            # Ajout des informations dans les combo box
            self.__clearOptions_()
            # @todo: Voir s'il ne serait pas possible d'utiliser addItems
            if (file_infos["nbpages"] == 1):
                pages = []
            else:
                pages = ["all"]
            pages.extend([str(x) for x in range(1, file_infos["nbpages"] + 1)])
            for page in pages:
                self.__basewidget_.page.addItem(page)
            dpis = ["max"]
            dpis.extend(["%dx%d" % (x, x) for x in [100, 200, 300, 400, 600] if x <= file_infos["dpi"][0]])
            for dpi in dpis:
                self.__basewidget_.resolution.addItem(dpi)
            if file_infos["samplesize"] == 24:
                self.__basewidget_.color.addItem("Color")
                self.__basewidget_.color.addItem("Black and White")
            else:
                self.__basewidget_.color.addItem("Black and White")
            
            self.__basewidget_.delete.setEnabled(True)
            self.__basewidget_.save.setEnabled(True)
            self.__basewidget_.format.setEnabled(True)
            self.__setFormat_(self.__basewidget_.format.currentText())
    
    def __clearOptions_(self):
        self.__basewidget_.page.clear()
        self.__basewidget_.resolution.clear()
        self.__basewidget_.color.clear()
    
    def __setFormat_(self, format):
        format = str(format).lower()
        if format == "pdf":
            self.__basewidget_.page.setEnabled(False)
        else:
            self.__basewidget_.page.setEnabled(True)
        
        self.__basewidget_.resolution.setEnabled(True)
        self.__basewidget_.color.setEnabled(True)
    
    def __deleteFile_(self):
        filename = self.currentFilename()
        if filename is not None:
            result = QMessageBox.question(self, "Confirmation of file deletion",
                                          "Do you really want to delete the file %s" \
                                          "from the scanner?" % filename, 
                                          QMessageBox.Yes, QMessageBox.No)
            if result == QMessageBox.Yes:
                self.__scanner_.deleteFile(filename)
                self.__refreshFolder_()

    def currentFilename(self):
        currentItem = self.__basewidget_.imageList.currentItem()
        # Vérification inutile, car le bouton delete est activ seulemen
        # s'il y a un item sélectionné, mais on ne sais jamais
        if currentItem is not None:
            return str(currentItem.text())
        
    def currentFolder(self):
        return str(self.__basewidget_.folder.currentText())
        
    def getFormat(self):
        return str(self.__basewidget_.format.currentText()).lower()
    
    def getDpi(self):
        dpi = str(self.__basewidget_.resolution.currentText())
        if dpi == "max":
            return None
        elif dpi == "100x100":
            return 100
        elif dpi == "200x200":
            return 200
        elif dpi == "300x300":
            return 300
        elif dpi == "400x400":
            return 400
        elif dpi == "600x600":
            return 600
    
    def getPages(self):
        if str(self.__basewidget_.page.currentText()) == "all":
            return [x for x in range(1, self.__scanned_files_[self.currentFilename()]["nbpages"] + 1)]
        else:
            return [int(str(self.__basewidget_.page.currentText()))]
    
    def getSamplesize(self):
        samplesize = str(self.__basewidget_.color.currentText())
        if samplesize == "Color":
            return 24
        else:
            # @todo: Regarder si c'est vraiment le noir et blanc (voir 8)
            return 1
    
    def __savePage_(self, filename, page, format, dpi, samplesize, save_filename):
        self.__scanner_.getFile(filename, save_filename, page, format, dpi, 
                                samplesize)

    def __saveFile_(self):
        filename = self.currentFilename()
        if filename is not None:
                save_filename = str(QFileDialog.getSaveFileName(self, "Saving scanned file", QDir.homePath()))
                if save_filename != "":
                    pages = self.getPages()
                    format = self.getFormat()
                    dpi = self.getDpi()
                    if dpi == None:
                        dpi = self.__scanned_files_[filename]["dpi"]
                    samplesize = self.getSamplesize()
                    
                    # @todo: Partir une thread pour le transfer
                    if format != "pdf" and len(pages) > 1:
                        for page in pages:
                            save_filename_x = "%s-%d%s" % (os.path.splitext(save_filename)[0], page, 
                                                           os.path.splitext(save_filename)[1])
                            self.__savePage_(filename, page, format, dpi, samplesize, save_filename_x)
                    else:
                        self.__savePage_(filename, pages[0], format, dpi, samplesize, save_filename)