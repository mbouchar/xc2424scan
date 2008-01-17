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
This library is able to communicate with the Xerox WorkCentre C2424
scanning protocol used by the binary windows application Xerox Scan Utility
used to retrieve the scanned images from the printer.

The library offers only some high-level functions. To have more informations
about the protocol used by the Xerox Scan Utility, please read the file
protocol.txt
"""

__all__ = ["XeroxC2424", "ProtectedError", "SocketError", "NoPreviewError"]

import os, socket
from xc2424scan import config

RECV_BUF_SIZE = 1500
FILE_BUF_SIZE = 10240

class NoPreviewError(Exception):
    pass

class ProtectedError(Exception):
    pass

class SocketError(Exception):
    pass

class XeroxC2424:

    FORMAT_TIFF = "tiff"
    FORMAT_GIF  = "gif"
    FORMAT_BMP  = "bmp"
    FORMAT_PDF  = "pdf"
    FORMAT_JPEG = "jpeg"

    def __init__(self):
        self.__socket_ = None
        self.connected = False
        self.__stop_ = False
    
    def stop(self):
        self.__stop_ = True

    def __del__(self):
        if self.connected is True:
            self.disconnect()

    def connect(self, address, port):
        if self.connected:
            self.disconnect()
        
        try:
            self.__socket_ = socket.socket()
            self.__socket_.connect((address, port))
        except socket.error:
            raise SocketError("Connection refused")
        self.connected = True

    def disconnect(self):
        self.__socket_.close()
        self.__socket_ = None
        self.connected = False
    
    #
    # Start of some useful functions
    #
    def __add_param_(self, command, param):
        if isinstance(param, int) or isinstance(param, long):
            command = "%s\t%d" % (command, param)
        elif isinstance(param, str):
            command = "%s\t%s" % (command, param)
        else:
            raise ValueError("Invalid parameter")

        return command

    def __send_command_(self, command, params = None):
        send_command = command
        if params is not None:
            if isinstance(params, list):
                for param in params:
                    send_command = self.__add_param_(send_command, param)
            else:
                send_command = self.__add_param_(send_command, params)

        self.__socket_.send("%s\n" % send_command)
        if config.DEBUG_LIB:
            print "S:", send_command
        result = self.__get_result_(RECV_BUF_SIZE)
        if config.DEBUG_LIB:
            if command != "sendblock":
                print result,
            else:
                print "received data"
        return result

    def __send_command_bool_(self, command, params = None):
        result = self.__send_command_(command, params).split("\n")[:-1]
        if result[0] != "ok":
            return False
        else:
            return True

    def __get_result_(self, buffer_size):
        try:
            result = self.__socket_.recv(buffer_size)
        except socket.timeout:
            raise SocketError("Socket timed out")
        return result
        
    def __get_received_size_(self, data):
        receivedSize = ""
        for character in data:
            if character != "\n":
                receivedSize += character
            else:
                size = receivedSize.split("\t")[1]
                if size == "eof":
                    return 0
                return int(size)

    def __receive_file_data_(self):
        received_size = RECV_BUF_SIZE
        file_data = ""
        while received_size != 0:
            cur_data = self.__send_command_("sendblock", FILE_BUF_SIZE)
            received_size = self.__get_received_size_(cur_data)
            cur_data = cur_data[len("sending\t%d\n" % received_size):]

            while len(cur_data) != received_size:
                cur_data += self.__get_result_(RECV_BUF_SIZE)

            file_data += cur_data
            
        return file_data

    def __save_file_data_(self, filename, progress_hook):
        save_file = file(filename, "w")
        
        received_size = RECV_BUF_SIZE
        while received_size != 0 and not self.__stop_:
            cur_data = self.__send_command_("sendblock", FILE_BUF_SIZE)
            received_size = self.__get_received_size_(cur_data)
            cur_data = cur_data[len("sending\t%d\n" % received_size):]

            while len(cur_data) != received_size:
                cur_data += self.__get_result_(RECV_BUF_SIZE)

            save_file.write(cur_data)
            progress_hook(received_size)
            
        save_file.close()

    #
    # Start of dumb low level commands
    #
    def __tellfilesize_(self):
        filesize = self.__send_command_("tellfilesize")
        try:
            return int(filesize.strip().split("\t")[1])
        except ValueError:
            raise ValueError("Unable to get a valid file size")
    
    def __setfile_(self, filename):
        if self.__send_command_bool_("setfile", filename) is not True:
            raise ValueError("%s is not a valid file" % filename)
        
    def __setusage_(self, usage):
        if self.__send_command_bool_("setusage", usage) is not True:
            raise ValueError("Error in the unknown command \"setusage\"")
        
    def __setformat_(self, format):
        if self.__send_command_bool_("setformat", format) is not True:
            raise ValueError("%s is not a valid image format" % format)

    def __setpage_(self, page = None):
        if page is None:
            if self.__send_command_bool_("setpage") is not True:
                raise ValueError("This format doesn't support multiple pages")
        else:
            if self.__send_command_bool_("setpage", page) is not True:
                raise ValueError("%d is not a valid page number" % page)

    def __setresolution_(self, resolution):
        if self.__send_command_bool_("setresolution", resolution) is not True:
            raise ValueError("%dx%d is not a valid resolution", 
                             (resolution, resolution))

    def __setsamplesize_(self, samplesize):
        if self.__send_command_bool_("setsamplesize", samplesize) is not True:
            raise ValueError("%d is not a valid sample size" % samplesize)
    
    #
    # Start of high level commands
    #
    def getFolders(self):
        """Returns the folders listing
        """
        result = self.__send_command_("listfolders").split("\n")[:-1]
        folderscount = int(result[0].split("\t")[1])
        result = result[1:]

        folders = []
        for folder in result:
            folders.append(folder.split("\t")[1])

        if len(folders) != folderscount:
            raise ValueError("Folder count is invalid: %s vs %s" % \
                             (folderscount, len(folders)))

        return folders

    def getFilesList(self):
        """Used to get the files listing
        
        filename, nbpages, resolution[0:horiz, 1:vert]
        
        @returns: The file listing
        @rtype: [ {str:object} ]
        """
        result = self.__send_command_("listfiles").split("\n")[:-1]
        filescount = int(result[0].split("\t")[1])
        result = result[1:]

        files = {}
        for curfile in result:
            curfile = curfile.split("\t")[1:]
            files[curfile[0]] = \
                {"size"      : int(curfile[1]),
                 "unknown2"  : int(curfile[2]),
                 "nbpages"   : int(curfile[3]), 
                 "dpi"       : [int(curfile[4]), int(curfile[5])],
                 "resolution": [int(curfile[6]), int(curfile[7])], 
                 "samplesize": int(curfile[8]),
                 "respreview"   : [int(curfile[9]), int(curfile[10])], 
                 "samplepreview": int(curfile[11])}

        return files

    def getCurrentFolder(self):
        """Used to get the name of the current folder
        
        @returns: The name of the current folder
        @rtype: str
        """
        result = self.__send_command_("tellfolder").split("\n")[:-1]
        return result[0].split("\t")[1]

    def setFolder(self, folder, password = None):
        """Set the current folder

        @param folder: The new folder name
        @type folder: str

        @returns: None
        @rtype: NoneType

        @raise ValueError: If the folder is invalid
        """
        if password is None:
            password = "-1"
            
        if self.__send_command_bool_("setpassword", password) == False:
            raise ProtectedError("Password must be a number between 1 and 9999")
                
        result = self.__send_command_("setfolder", folder)[:-1].split("\t")
        if result[0] == "error":
            if result[1] == "protected":
                raise ProtectedError("The folder %s is password protected" \
                                     % folder)
            else:
                raise ValueError("The folder %s doesn't exists" % folder)

    def getFile(self, filename, save_filename, pages = None, 
                format = FORMAT_TIFF, dpi = [100, 100], samplesize = 24,
                newpage_hook = None, progress_hook = None):
        """Get a file from the scanner

        @param filename: The file name of the file
        @param page: The page number to get (None for all (only with a pdf
            file))
        @param format: The file format to get (png is supported, but converted
            from tiff on the client side)
        @param resolution: The horizontal and vertical resolutions of the file. 
            The minimum resolution is used by default to be sure there will be
            no errors

        @type filename: str
        @type page: int
        @type format: str
        @param resolution: [int, int]

        @returns: None
        @rtype: NoneType

        @raise ValueError: If a parameter is invalid
        """
        if format == self.FORMAT_PDF:
            pages = [-1]

        for page in pages:
            # Check if the user canceled the transfer
            if self.__stop_:
                self.__stop_ = False
                return

            # Set the filename
            self.__setfile_(filename)
            # Unknown
            self.__setusage_([1, 2])
            # Set the file format
            self.__setformat_(format)
            # Set the page
            if format == self.FORMAT_PDF:
                # If we are saving a pdf file, we have to get all pages at the
                # same time
                self.__setpage_()
            else:
                self.__setpage_(page)

            # Set the resolution
            self.__setresolution_(dpi)
            # Set the sample size
            self.__setsamplesize_(samplesize)

            # Send new page signal
            if format in ["tiff", "bmp"]:    
                newpage_hook(page, self.__tellfilesize_())
            else:
                newpage_hook(page)

            # If we have multiple pages, we append the page number at the end
            if len(pages) > 1:
                save_filename_x = "%s-p%d%s" % \
                                  (os.path.splitext(save_filename)[0], page, 
                                   os.path.splitext(save_filename)[1])
            else:
                save_filename_x = save_filename

            # Save the requested pages
            self.__save_file_data_(save_filename_x, progress_hook)

    def getPreview(self, filename):
        """Get the preview of a file
        
        @param filename: The file name of the file
        @type filename: str
        
        @returns: The data of the file preview
        @rtype: str
        """
        # Set the filename
        self.__setfile_(filename)
        # Previews are always in bmp (at least in the Xerox scanning application)
        self.__setformat_(self.FORMAT_BMP)
        # The preview page is -1
        try:
            self.__setpage_(-1)
        except ValueError:
            raise NoPreviewError()

        return self.__receive_file_data_()

    def deleteFile(self, filename):
        """Delete a file from the WorkCentre hard disk
        
        @param filename: The name of the file to delete
        @type filename: str
        
        @returns: None
        @rtype: NoneType
        """
        if self.__send_command_bool_("deletefile", filename) is not True:
            raise ValueError("The filename is not valid")
