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

from xc2424scan.threadedscanlib import ThreadedXeroxC2424
from xc2424scan.scanlib import ProtectedError, SocketError, NoPreviewError

from xc2424scan.ui.widgets.scanwidgetbase import Ui_ScanWidgetBase

class ScanWidget(QWidget):
    # @todo: Les widgets doivent être désactivés par défaut
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.__basewidget_ = Ui_ScanWidgetBase()
        self.__basewidget_.setupUi(self)
        
        self.__threadedscanner_ = ThreadedXeroxC2424()
        
        # List of files available on the scanner
        self.__scanned_files_ = None
        # Last folder visited (see __showFolder_)
        self.__last_folder_ = None
        # Nombre de previews affichés
        self.__nb_preview_received_ = 0
        # Dernier répertoire visité
        self.__old_folder_ = "Public"
        
        # UI: Boutons
        QObject.connect(self.__basewidget_.refresh, SIGNAL("clicked()"),
                        self.__ui_refresh_clicked_)
        QObject.connect(self.__basewidget_.delete, SIGNAL("clicked()"),
                        self.__ui_delete_clicked_)
        QObject.connect(self.__basewidget_.save, SIGNAL("clicked()"),
                        self.__ui_save_clicked_)
        # UI: Options modifiées
        QObject.connect(self.__basewidget_.folder, SIGNAL("activated(const QString&)"),
                        self.__ui_folder_currentChanged_)
        QObject.connect(self.__basewidget_.imageList, SIGNAL("currentTextChanged(const QString&)"),
                        self.__ui_imageList_currentChanged_)
        QObject.connect(self.__basewidget_.format, SIGNAL("currentIndexChanged(const QString&)"),
                        self.__ui_format_currentChanged_)
        
        # Signals emited from threads
        QObject.connect(self.__threadedscanner_, SIGNAL("foldersList()"),
                        self.__foldersListReceived_)
        QObject.connect(self.__threadedscanner_, SIGNAL("filesList()"),
                        self.__filesListReceived_)
        QObject.connect(self.__threadedscanner_, SIGNAL("currentFolder(const QString&)"),
                        self.__currentFolderReceived_)
        QObject.connect(self.__threadedscanner_, SIGNAL("folderSet(const QString&)"),
                        self.__folderSet_)
        QObject.connect(self.__threadedscanner_, SIGNAL("folderProtected(const QString&)"),
                        self.__folderProtected_)
        QObject.connect(self.__threadedscanner_, SIGNAL("fileReceived(const QString&)"),
                        self.__fileReceived_)
        QObject.connect(self.__threadedscanner_, SIGNAL("previewReceived(const QString&)"),
                        self.__previewReceived_)
        QObject.connect(self.__threadedscanner_, SIGNAL("fileDeleted(const QString&)"),
                        self.__fileDeleted_)
        QObject.connect(self.__threadedscanner_, SIGNAL("connectedToScanner()"),
                        self.__connectedToScanner_)

    #
    # Fonctions connectées aux threads
    #
    def __currentFolderReceived_(self, folder):
        pass
    
    def __folderSet_(self, folder):
        self.__refreshPreviews_()
    
    def __folderProtected_(self, folder):
        # @todo: si on appuye sur cancel, il faut remettre l'ancien répertoire dans la liste
        # @todo: on doit désactiver la liste lors de la récupération des previews
        folder = str(folder)
        
        password, result = QInputDialog.getText(self, "Accessing a protected folder",
                                        "Please enter the password for the protected " \
                                        "folder %s" % folder, QLineEdit.Password)

        if result is True:
            self.__threadedscanner_.setFolder(folder, str(password))
                
    def __fileReceived_(self, filename):
        pass
    
    def __previewReceived_(self, filename):
        self.__nb_preview_received_ += 1
        
        filename = str(filename)
        preview = self.__threadedscanner_.previews[filename]
        del self.__threadedscanner_.previews[filename]

        # Création du pixmap
        pixmap = QPixmap()
        if preview == None:
            # @todo: Le prefix peut changer
            pixmap.load("/usr/share/xc2424scan/nopreview.png")
        else:
            pixmap.loadFromData(preview)
            
        # creation of a black border
        painter = QPainter()
        painter.setPen(Qt.black);
        painter.begin(pixmap)
        width = self.__scanned_files_[filename]["respreview"][0] - 1
        height = self.__scanned_files_[filename]["respreview"][1] - 1
        painter.drawRect(QRect(0, 0, width, height))
        painter.end()

        # Ajout de l'icône à la liste
        items = self.__basewidget_.imageList.findItems(filename, Qt.MatchExactly)
        items[0].setIcon(QIcon(pixmap))

        if self.__nb_preview_received_ == len(self.__scanned_files_):
            self.__basewidget_.refresh.setEnabled(True)
            if self.__basewidget_.imageList.currentItem() != None:
                self.__basewidget_.delete.setEnabled(True)
                self.__basewidget_.save.setEnabled(True)
    
    def __fileDeleted_(self, filename):
        items = self.__basewidget_.imageList.findItems(filename, Qt.MatchExactly)
        item = self.__basewidget_.imageList.takeItem(self.__basewidget_.imageList.row(items[0]))
        del item
    
    def __connectedToScanner_(self):
        # Affichage du répertoire public
        self.__basewidget_.imageList.clear()
        self.__threadedscanner_.getFolders()
        self.__threadedscanner_.wait()
        self.__threadedscanner_.getFiles()
        self.__threadedscanner_.wait()

    def __foldersListReceived_(self):
        for folder in self.__threadedscanner_.folders:
            self.__basewidget_.folder.addItem(folder)
            
        self.setEnabled(True)

    def __filesListReceived_(self):
        self.__scanned_files_ = self.__threadedscanner_.files
        
        # Récupération du preview des images
        # @todo: Preview avec un filename non fixe
        if len(self.__scanned_files_) != 0:
            filenames = self.__scanned_files_.keys()
            filenames.sort()
            # Affichage des fichiers
            pixmap = QPixmap()
            pixmap.load("/usr/share/xc2424scan/waitingpreview.png")

            for filename in filenames:
                self.__basewidget_.imageList.addItem(QListWidgetItem(QIcon(pixmap), filename))

            # Récupération des previews
            self.__nb_preview_received_ = 0
            self.__threadedscanner_.getPreviews(filenames)
        else:
            self.__basewidget_.refresh.setEnabled(True)
            self.__basewidget_.folder.setEnabled(True)
    
    #
    # Fonctions connectées à l'interface graphique
    #
    def __ui_refresh_clicked_(self):
        """
        - Désactive l'ensemble du ui
        - Supprime tous les preview
        - Affiche tous les previews
        """
        self.__refreshPreviews_()

    def __ui_delete_clicked_(self):
        filename = self.currentFilename()
        if filename is not None:
            result = QMessageBox.question(self, "Confirmation of file deletion",
                                          "Do you really want to delete the file %s " \
                                          "from the scanner?" % filename, 
                                          QMessageBox.Yes, QMessageBox.No)
            if result == QMessageBox.Yes:
                self.__threadedscanner_.deleteFile(filename)

    def __ui_save_clicked_(self):
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

    def __ui_folder_currentChanged_(self, folder):
        folder = str(folder)
        self.__threadedscanner_.setFolder(folder)

    def __ui_imageList_currentChanged_(self, filename):
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

            if not self.__threadedscanner_.isRunning():
                self.__basewidget_.delete.setEnabled(True)
                self.__basewidget_.save.setEnabled(True)
            self.__basewidget_.format.setEnabled(True)
            self.__ui_format_currentChanged_(self.__basewidget_.format.currentText())
    
    def __ui_format_currentChanged_(self, format):
        format = str(format).lower()
        if format == "pdf":
            self.__basewidget_.page.setEnabled(False)
        else:
            self.__basewidget_.page.setEnabled(True)
        
        self.__basewidget_.resolution.setEnabled(True)
        self.__basewidget_.color.setEnabled(True)
    
    #
    # Autres fonctions
    #
    def __refreshFilesList_(self):
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
    
    def __clearOptions_(self):
        self.__basewidget_.page.clear()
        self.__basewidget_.resolution.clear()
        self.__basewidget_.color.clear()
    
    def __refreshPreviews_(self):
        self.__basewidget_.refresh.setEnabled(False)
        self.__basewidget_.delete.setEnabled(False)
        self.__basewidget_.save.setEnabled(False)
        self.__basewidget_.folder.setEnabled(False)
        self.__basewidget_.imageList.clear()

        self.__threadedscanner_.getFiles()
        self.__threadedscanner_.wait()

    def __savePage_(self, filename, page, format, dpi, samplesize, save_filename):
        self.__scanner_.getFile(filename, save_filename, page, format, dpi, 
                                samplesize)

    #
    # API public
    #
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

    def connectToScanner(self, host, port):
        self.__threadedscanner_.connectToScanner(host, port)
    
    def disconnect(self):
        self.__threadedscanner_.disconnect()
