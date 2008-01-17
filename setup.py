# -*- coding: utf-8 -*-

#   This file is part of the xc2424scan project
#   Copyright (C) 2006 Mathieu Bouchard <mbouchar@bioinfo.ulaval.ca>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
Fichier permettant d'utiliser distutils pour installer le logiciel xc2424scan

@author: Mathieu Bouchard
@version: 1.0
"""

from distutils.core import setup
import sys

# Ajout du path vers le fichier version.py
sys.path.insert(0, 'src')
from xc2424scan import version

PROGRAM = version.__program__
VERSION = version.__version__

if __name__ == "__main__":
    # Installation de xc2424scan
    setup(name             = version.__program__,
          version          = version.__version__,
          description      = version.__description__,
          long_description = version.__long_description__,
          author           = version.__authors__[0]["name"],
          author_email     = version.__authors__[0]["email"],
          maintainer       = version.__maintainer__["name"],
          maintainer_email = version.__maintainer__["email"],
          url              = version.__url__,
          license          = version.__license__,
          platforms        = version.__platforms__,
          packages         = ["xc2424scan", 
                              "xc2424scan/ui",
                              "xc2424scan/ui/widgets"],
          package_dir      = {"xc2424scan": "src/xc2424scan",
                              "xc2424scan/ui": "src/xc2424scan/ui",
                              "xc2424scan/ui/widgets": "src/xc2424scan/ui/widgets"},
          scripts          = ["exec/xc2424scan"],
          data_files       = [("share/xc2424scan", ["data/nopreview.png",
                                                    "data/waitingpreview.png"]),
                              ("share/applications", ["data/xc2424scan.desktop"])],
         )
