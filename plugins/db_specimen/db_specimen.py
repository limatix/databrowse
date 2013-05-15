#!/usr/bin/env python
###############################################################################
## Databrowse:  An Extensible Data Management Platform                       ##
## Copyright (C) 2012-2013 Iowa State University                             ##
##                                                                           ##
## This program is free software: you can redistribute it and/or modify      ##
## it under the terms of the GNU General Public License as published by      ##
## the Free Software Foundation, either version 3 of the License, or         ##
## (at your option) any later version.                                       ##
##                                                                           ##
## This program is distributed in the hope that it will be useful,           ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of            ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             ##
## GNU General Public License for more details.                              ##
##                                                                           ##
## You should have received a copy of the GNU General Public License         ##
## along with this program.  If not, see <http://www.gnu.org/licenses/>.     ##
###############################################################################
""" plugins/renderers/db_xml_generic.py - Default Text Renderer """

import os
from lxml import etree
from renderer_support import renderer_class


class db_specimen(renderer_class):
    """ Default Renderer - Basic Output for Any XML File """

    _namespace_uri = "http://thermal.cnde.iastate.edu/specimen"
    _namespace_local = "specimen"
    _default_content_mode = "full"
    _default_style_mode = "view_specimen_data"
    _default_recursion_depth = 2

    def getContent(self):
        if self._caller == "databrowse":
            f = open(self._fullpath, 'r')
            xml = etree.parse(f)
            f.close()
            filerelpath = os.path.join(os.path.dirname(self._relpath), os.path.splitext(os.path.basename(self._relpath))[0] + "_files")
            filefullpath = os.path.abspath(self._web_support.dataroot + '/' + filerelpath)
            if os.path.exists(filefullpath) and self._style_mode == "view_specimen_data":
                import db_directory.db_directory as db_directory_module
                renderer = db_directory_module.db_directory(filerelpath, filefullpath, self._web_support, self._handler_support, "db_specimen", "db_directory", style_mode="empty")
                content = renderer.getContent()
                xmlroot = xml.getroot()
                xmlroot.append(content)
            else:
                xmlroot = xml.getroot()
            return xmlroot
        else:
            return None
        pass

    pass
