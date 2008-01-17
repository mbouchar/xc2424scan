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
This is the module used to get the application configuration

@author: Mathieu Bouchard
@version: 0.1
"""

__all__ = ["Config"]

from ConfigParser import ConfigParser, NoSectionError, NoOptionError, \
                         DuplicateSectionError
import sys, os

DEBUG_GUI = False
DEBUG_LIB = False

# @todo: Utiliser OptionParser
if "--debug-lib" in sys.argv or "--debug" in sys.argv:
    DEBUG_LIB = True
if "--debug-gui" in sys.argv or "--debug" in sys.argv:
    DEBUG_GUI = True

FILES_PREFIX = "/usr/share/xc2424scan/"
NO_PREVIEW_FILENAME = os.path.join(FILES_PREFIX, "nopreview.png")
WAITING_PREVIEW_FILENAME = os.path.join(FILES_PREFIX, "waitingpreview.png")

# If xc2424scan is not installed, use the files from the source directory
if not os.path.isfile(NO_PREVIEW_FILENAME):
    NO_PREVIEW_FILENAME = "data/nopreview.png"
if not os.path.isfile(WAITING_PREVIEW_FILENAME):
    WAITING_PREVIEW_FILENAME = "data/waitingpreview.png"

class Config(object):
    """Config file reader"""
    
    GROUP   = "xc2424scan"
    ADDRESS = "address"
    PORT    = "port"
    DEFAULT_PORT = 14882
    
    def __init__(self, configfile = ["/etc/xc2424scan", "~/.xc2424scan"]):
        self.__config_file_ = [os.path.expanduser(x) for x in configfile]
        self.__config_ = ConfigParser()

        self.__address_ = None
        self.__port_ = None
        
        self.reload()
        
    def __get_(self, key):
        try:
            return self.__config_.get(self.GROUP, key)
        except (NoSectionError, NoOptionError):
            return None
    
    def __modify_(self, key, value):
        """Écriture d'une clé dans le fichier de configuration

        Si la clé existe, sa valeur est écrasée par la nouvelle valeur
        Si la clé et/ou le groupe n'existent pas, ils sont créés
        
        @param key: La clé à écrire
        @param value: La valeur de la clé
        
        @type key: str
        @type value: str

        @return: None
        @rtype: NoneType
        """
        # Ajout de la section
        try:
            self.__config_.add_section(self.GROUP)
        except DuplicateSectionError:
            pass
        
        self.__config_.set(self.GROUP, key, str(value))
        # Normalement, les modifications sont déjà sauvegardées, mais on
        # ne prendra pas de chance pour être sûr qu'aucune information n'est
        # perdue
        if isinstance(self.__config_file_, str):
            config_file = file(self.__config_file_, "w")
        else:
            config_file = file(os.path.expanduser("~/.xc2424scan"), "w")
        self.__config_.write(config_file)

    def __get_address_(self):
        return self.__address_
    def __set_address_(self, address):
        self.__modify_("address", address)
        self.__address_ = address
    
    def __get_port_(self):
        return self.__port_
    def __set_port_(self, port):
        self.__modify_("port", port)
        self.__port_ = port
        
    def reload(self):
        # Lecture du fichier
        self.__config_.read(self.__config_file_)
        
        # Récupération des valeurs
        self.__address_ = self.__get_(self.ADDRESS)
        try:
            self.__port_ = int(self.__get_(self.PORT))
        except (TypeError, ValueError):
            self.__port_ = self.DEFAULT_PORT

    def save(self):
        pass
    
    address = property(__get_address_, __set_address_)
    port = property(__get_port_, __set_port_)
