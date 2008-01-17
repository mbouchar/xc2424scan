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
"""

__all__ = ["ScanWidget"]

from PyQt4.QtCore import QDir, QObject, QRect, Qt, SIGNAL
from PyQt4.QtGui import QWidget, QFileDialog, QListWidgetItem, QPixmap, \
                        QIcon, QMessageBox, QInputDialog, QLineEdit, QPainter, \
                        QProgressDialog, QMessageBox, QSizePolicy
import os

from xc2424scan import config
from xc2424scan.threadedscanlib import ThreadedXeroxC2424
from xc2424scan.scanlib import ProtectedError, SocketError, NoPreviewError

from xc2424scan.ui.widgets.scanwidgetbase import Ui_ScanWidgetBase

# @todo: Il est possible de savoir le nombre de pages des pdfs aussi avec un peu de travail
class ProgressDialog(QProgressDialog):
    def __init__(self, parent = None):
        QProgressDialog.__init__(self, parent)
        self.setWindowTitle(_("Downloading"))

        # Top level fixed size dialog
        self.setWindowModality(Qt.WindowModal)
        self.setFixedSize(self.size())
        # Do not close at 100%
        self.setAutoClose(False)
        self.setAutoReset(False)
        
        self.__nbr_pages_ = -1
    
    def setNbrPages(self, nbr_pages):
        self.__nbr_pages_ = nbr_pages

    def newpage(self, current_page, file_size):
        if self.isVisible():
            # Set progress range
            self.setValue(0)
            self.setRange(0, file_size)
            # Set label text
            if self.__nbr_pages_ == -1:
                self.setLabelText(_("Getting file"))
            elif self.__nbr_pages_ == 1:
                self.setLabelText(_("Getting page %d") % current_page)
            else:
                self.setLabelText(_("Getting page %d of %d") % \
                                  (current_page, self.__nbr_pages_))
    
    def progress(self, received_size):
        if self.isVisible():
            self.setValue(self.value() + received_size)

class ScanWidget(QWidget):
    """The main scanning widget"""
    
    def __init__(self, parent = None, debug = False):
        """Create a new scanning widget
        
        @param parent: The parent widget
        @type parent: QWidget
        @param debug: verbose mode or not
        @type debug: bool
        """
        QWidget.__init__(self, parent)
        self.__basewidget_ = Ui_ScanWidgetBase()
        self.__basewidget_.setupUi(self)
        
        # The threaded scanner object
        self.__scanner_ = ThreadedXeroxC2424(debug)
        
        # List of files available on the scanner
        self.__scanned_files_ = None
        # Last folder visited
        self.__old_folder_ = "Public"
        
        # UI: Buttons
        QObject.connect(self.__basewidget_.refresh, SIGNAL("clicked()"),
                        self.__ui_refresh_clicked_)
        QObject.connect(self.__basewidget_.delete, SIGNAL("clicked()"),
                        self.__ui_delete_clicked_)
        QObject.connect(self.__basewidget_.save, SIGNAL("clicked()"),
                        self.__ui_save_clicked_)
        # UI: An option has been modified
        QObject.connect(self.__basewidget_.folder,
                        SIGNAL("activated(const QString&)"),
                        self.__ui_folder_currentChanged_)
        # UI: List widget
        QObject.connect(self.__basewidget_.imageList,
                        SIGNAL("currentTextChanged(const QString&)"),
                        self.__ui_imageList_currentChanged_)
        QObject.connect(self.__basewidget_.format,
                        SIGNAL("currentIndexChanged(const QString&)"),
                        self.__ui_format_currentChanged_)
        
        # Signals emited from threads
        QObject.connect(self.__scanner_, SIGNAL("foldersList()"),
                        self.__foldersListReceived_)
        QObject.connect(self.__scanner_, SIGNAL("filesList()"),
                        self.__filesListReceived_)
        QObject.connect(self.__scanner_, SIGNAL("folderSet(const QString&)"),
                        self.__folderSetReceived_)
        QObject.connect(self.__scanner_, SIGNAL("folderProtected(const QString&)"),
                        self.__folderProtectedReceived_)
        QObject.connect(self.__scanner_, SIGNAL("fileReceived(const QString&)"),
                        self.__fileReceived_)
        QObject.connect(self.__scanner_, SIGNAL("previewReceived(const QString&)"),
                        self.__previewReceived_)
        QObject.connect(self.__scanner_, SIGNAL("allPreviewReceived()"),
                        self.__allPreviewReceived_)
        QObject.connect(self.__scanner_, SIGNAL("fileDeleted(const QString&)"),
                        self.__fileDeletedReceived_)
        QObject.connect(self.__scanner_, SIGNAL("connectedToScanner()"),
                        self.__connectedToScannerReceived_)
        
        QObject.connect(self.__scanner_, SIGNAL("scanlibError(const QString&)"),
                        self.__scanlibErrorReceived)

        # Progress dialog        
        self.__progress_ = ProgressDialog(self)
        QObject.connect(self.__scanner_, SIGNAL("newPage(int, int)"),
                        self.__progress_.newpage)
        QObject.connect(self.__scanner_, SIGNAL("progress(int)"),
                        self.__progress_.progress)
        QObject.connect(self.__progress_, SIGNAL("canceled()"),
                        self.__ui_progress_cancelled_)

        self.__lock_()

    #
    # Methods connected to thread signals
    #
    def __scanlibErrorReceived(self, text):
        """Called when there is an error in the scan library
        
        @param text: The text of the error
        @type text: str
        """
        if self.__progress_.isVisible():
            self.__progress_.close()
        QMessageBox.critical(self, "Critical error", text)
        if self.__scanner_.connected:
            self.__unlock_()
    
    def __connectedToScannerReceived_(self):
        """Called when we are connected to a new scanner"""
        # Show the public directory
        print "<-- Connected to scanner"
        # Clear the list of files and request the available folders
        self.__basewidget_.imageList.clear()
        self.__scanner_.getFolders()

    def __folderSetReceived_(self, folder):
        """Called when we have changed the current folder
        
        @param folder: The folder name
        @type folder: str
        """
        print "<-- Folder has been set:", str(folder)
        # Save old folder
        self.__old_folder_ = str(folder)

        # Refresh the contents of the folder
        self.__refreshPreviews_()
    
    def __folderProtectedReceived_(self, folder):
        """Called when we are trying to access a protected folder
        
        @param folder: The folder name
        @type folder: str
        """
        print "<-- Protected folder:", folder
        folder = str(folder)
        
        password, result = QInputDialog.getText(self, "Accessing a protected folder",
                                        "Please enter the password for the protected " \
                                        "folder %s" % folder, QLineEdit.Password)

        if result is True:
            self.__scanner_.setFolder(folder, str(password))
        else:
            folder_index = self.__basewidget_.folder.findText(self.__old_folder_)
            self.__basewidget_.folder.setCurrentIndex(folder_index)
            self.__unlock_()
                
    def __fileReceived_(self, filename):
        """Called when a file tranfert has been successfully completed
        
        @param filename: The file name
        @type filename: str
        """
        print "<-- Received file:", filename
        # Reset the progress dialog and unlock the widget
        self.__progress_.hide()
        self.__unlock_()
    
    def __allPreviewReceived_(self):
        """Received when we have received all previews"""
        print "<-- All previews received"
        self.__unlock_()
        self.__basewidget_.imageList.setCurrentItem(self.__basewidget_.imageList.item(0))

    def __previewReceived_(self, filename):
        """Received when a preview has been received
        
        @param filename: The filename of the preview
        @type filename: str
        """
        print "<-- Preview received:", filename
        filename = str(filename)
        preview = self.__scanner_.previews[filename]
        del self.__scanner_.previews[filename]

        # Create the pixmap item
        pixmap = QPixmap()
        if preview == None:
            pixmap.load(config.NO_PREVIEW_FILENAME)
        else:
            pixmap.loadFromData(preview)
            
        # Add a black border
        self.__add_black_border_(pixmap)

        # Add the new icon to the list
        items = self.__basewidget_.imageList.findItems(filename, Qt.MatchExactly)
        items[0].setIcon(QIcon(pixmap))
    
    def __fileDeletedReceived_(self, filename):
        """Called when a file has been deleted
        
        @param filename: The name of the deleted file
        @type filename: str
        """
        print "<-- File deleted:", filename
        # Remove the deleted item from the list
        items = self.__basewidget_.imageList.findItems(filename, Qt.MatchExactly)
        item = self.__basewidget_.imageList.takeItem(self.__basewidget_.imageList.row(items[0]))
        del item
        # Unlock the widget
        self.__unlock_()
    
    def __foldersListReceived_(self):
        """Called when the folders listing has arrived"""
        print "<-- Received folder listing"
        # Add the folders to the list of folders
        for folder in self.__scanner_.folders:
            self.__basewidget_.folder.addItem(folder)
        # Refresh the files of the current folder
        self.__refreshPreviews_()

    def __filesListReceived_(self):
        """Called when the files listing of the current folder has arrived"""
        print "<-- Received files listing"
        self.__scanned_files_ = self.__scanner_.files
        
        # Add the files to the list and request their previews
        if len(self.__scanned_files_) != 0:
            # Sort by filename (wich is also by date)
            filenames = self.__scanned_files_.keys()
            filenames.sort()
            # Create the Waiting for preview pixmap
            pixmap = QPixmap()
            pixmap.load(config.WAITING_PREVIEW_FILENAME)
            self.__add_black_border_(pixmap)

            # Add the files to the list
            for filename in filenames:
                self.__basewidget_.imageList.addItem(QListWidgetItem(QIcon(pixmap), filename))

            # Request the previews
            print "--> Requesting previews"
            self.__scanner_.getPreviews(filenames)
        else:
            self.__unlock_()
    
    #
    # Methods connected to the UI
    #
    def __ui_refresh_clicked_(self):
        """Called when the user activates the refresh button
        
        This method clears the files list and request the current files list
        again
        """
        # Refresh the folder contents
        self.__refreshPreviews_()

    def __ui_delete_clicked_(self):
        """Called when the user activates the delete button
        
        This method delete the current selected file
        """
        print "--> Deleting file"
        filename = self.currentFilename()
        if filename is not None:
            result = QMessageBox.question(self, "Confirmation of file deletion",
                                          "Do you really want to delete the file %s " \
                                          "from the scanner?" % filename, 
                                          QMessageBox.Yes, QMessageBox.No)
            if result == QMessageBox.Yes:
                self.__scanner_.deleteFile(filename)
        else:
            print "WARNING: No file selected (save), this should not happen"

    def __ui_save_clicked_(self):
        """Called when the user activates the save button
        
        This method ask for a filename and download the selected pages
        """
        print "--> Saving file"
        filename = self.currentFilename()
        
        # Check if a file has been selected
        if filename is not None:
            # Ask for filename
            save_filter = self.__get_format_filter_()
            default_save_filename = os.path.join(str(QDir.homePath()), 
                                                 "%s.%s" % (os.path.splitext(filename)[0],
                                                            self.getFormat()))
            save_filename = str(QFileDialog.getSaveFileName(self, "Saving scanned file",
                                                            default_save_filename,
                                                            save_filter))
            if save_filename != "":
                self.__lock_()
                # Add file format if not specified
                if os.path.splitext(save_filename)[1] == "":
                    save_filename += ".%s" % self.getFormat()
                # Call the saving thread method
                pages = self.getPages()
                format = self.getFormat()
                dpi = self.getDpi()
                if dpi == None:
                    dpi = self.__scanned_files_[filename]["dpi"]
                samplesize = self.getSamplesize()
                self.__scanner_.getFile(filename, save_filename, pages,
                                        format, dpi, samplesize)
                # Show the progress dialog (only works for tiff and bmp)
                if self.getFormat() in ["tiff", "bmp"]:
                    self.__progress_.setLabelText(_("Waiting for transfer to begin"))
                    self.__progress_.setNbrPages(len(pages))
                    self.__progress_.setValue(0)
                    self.__progress_.show()
                else:
                    # @todo: Do something for other formats
                    pass
        else:
            print "WARNING: No file selected (save), this should not happen"

    def __ui_folder_currentChanged_(self, folder):
        """Called when the current folder has been changed
        
        If the user has selected another directory, we need to list the contents
        of this directory
        """
        print "--> Changing folder"
        folder = str(folder)
        if folder != self.__old_folder_:
            self.__lock_()
            # Request the new folder        
            self.__scanner_.setFolder(folder)

    def __ui_imageList_currentChanged_(self, filename):
        """Called when the user select an image in the image list
        
        @param filename: The file name of the selected file
        @type filename: str
        """
        filename = str(filename)
        print "--- Selected file: \"%s\"" % filename
        
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
            # Show basic informations
            self.__basewidget_.info_nbPages.setText(str(file_infos["nbpages"]))
            self.__basewidget_.info_dpi.setText("%dx%d dpi" % \
                                                (file_infos["dpi"][0],
                                                 file_infos["dpi"][1]))
            self.__basewidget_.info_resolution.setText("%dx%d" % \
                                                       (file_infos["resolution"][0],
                                                        file_infos["resolution"][1]))
            
            # Create file options
            self.__clearOptions_()
            # Add pages
            pages = []
            if file_infos["nbpages"] > 1:
                pages.append("all")
            pages.extend([str(x) for x in range(1, file_infos["nbpages"] + 1)])
            self.__basewidget_.page.addItems(pages)
            # Add dpi
            dpis = ["max"]
            dpis.extend(["%dx%d" % (x, x) for x in [100, 200, 300, 400, 600]
                         if x <= file_infos["dpi"][0]])
            self.__basewidget_.resolution.addItems(dpis)
            # Add samplesize
            if file_infos["samplesize"] == 24:
                self.__basewidget_.color.addItem("Color")
            if file_infos["samplesize"] >= 8:
                self.__basewidget_.color.addItem("Grayscale")
            self.__basewidget_.color.addItem("Black & White")

            # Enable buttons
            self.__basewidget_.delete.setEnabled(True)
            self.__basewidget_.save.setEnabled(True)
            # Enable options
            self.__basewidget_.format.setEnabled(True)
            self.__basewidget_.resolution.setEnabled(True)
            self.__basewidget_.color.setEnabled(True)
            self.__ui_format_currentChanged_(self.__basewidget_.format.currentText())
    
    def __ui_format_currentChanged_(self, format):
        """Called when file format has changed
        
        If the file format is pdf, we cannot select a page. If it is not pdf, we
        need to enable the page selector
        """
        format = str(format).lower()
        if format == "pdf":
            self.__basewidget_.page.setCurrentIndex(0)
            self.__basewidget_.page.setEnabled(False)
        else:
            self.__basewidget_.page.setEnabled(True)
    
    # @todo: Send a signal to the thread asking to stop correctly instead, because we get garbage now
    def __ui_progress_cancelled_(self):
        """Called when the user click on the progress cancel button"""
        print "--- Cancelled saving"
        self.__scanner_.terminate()
        self.__scanner_.wait()
        self.__unlock_()
        print "WARNING: Protocol screwed, exiting"
        import sys
        sys.exit(0)
    
    #
    # Other methods
    #
    def __get_format_filter_(self):
        format = self.getFormat()
        if format == "tiff":
            filter = _("TIFF images (*.tif *.tiff)")
        elif format == "gif":
            filter = _("GIF images (*.gif)")
        elif format == "jpeg":
            filter = _("JPEG images (*.jpg *.jpeg)")
        elif format == "bmp":
            filter = _("BMP images (*.bmp)")
        elif format == "pdf":
            filter = _("PDF files (*.pdf)")
        else:
            filter = ""
        return filter + ";;All files (*)"

    def __add_black_border_(self, pixmap):
        """Add a black border around a pixmap
        
        @param pixmap: The pixmap
        @type pixmap: QPixmap
        """
        painter = QPainter()
        painter.setPen(Qt.black);
        painter.begin(pixmap)
        painter.drawRect(QRect(0, 0, pixmap.width() - 1, pixmap.height() - 1))
        painter.end()

    def __refreshPreviews_(self):
        print "--> Refreshing previews"
        self.__basewidget_.imageList.clear()
        self.__lock_()

        self.__scanner_.getFilesList()

    def __clearOptions_(self):
        self.__basewidget_.page.clear()
        self.__basewidget_.resolution.clear()
        self.__basewidget_.color.clear()
    
    def __lock_(self):
        self.__basewidget_.refresh.setEnabled(False)
        self.__basewidget_.folder.setEnabled(False)
        self.__basewidget_.imageList.setEnabled(False)

        self.__basewidget_.save.setEnabled(False)
        self.__basewidget_.delete.setEnabled(False)
        self.__basewidget_.format.setEnabled(False)
        self.__basewidget_.page.setEnabled(False)
        self.__basewidget_.resolution.setEnabled(False)
        self.__basewidget_.color.setEnabled(False)

    def __unlock_(self):
        self.__basewidget_.refresh.setEnabled(True)
        self.__basewidget_.folder.setEnabled(True)
        self.__basewidget_.imageList.setEnabled(True)
        
        if self.currentFilename() is not None:
            self.__basewidget_.save.setEnabled(True)
            self.__basewidget_.delete.setEnabled(True)
            self.__basewidget_.format.setEnabled(True)
            self.__basewidget_.page.setEnabled(True)
            self.__basewidget_.resolution.setEnabled(True)
            self.__basewidget_.color.setEnabled(True)

    #
    # API public
    #
    def currentFilename(self):
        currentItem = self.__basewidget_.imageList.currentItem()
        # Vérification inutile, car le bouton delete est activé seulement
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
    
    # @todo: When saving more than one page, the sample size is not working
    def getSamplesize(self):
        samplesize = str(self.__basewidget_.color.currentText())
        # 24 bits color
        if samplesize == "Color":
            return 24
        # 8 tones grayscale
        elif samplesize == "Grayscale":
            return 8
        # black and white
        else:
            return 1

    def connectToScanner(self, host, port):
        print "--> Connecting to scanner"
        self.__scanner_.connectToScanner(host, port)
    
    def disconnect(self):
        print "--> Disconnecting from scanner"
        self.__scanner_.disconnect()
