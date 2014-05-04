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
import StringIO
from lxml import etree
from databrowse.support.renderer_support import renderer_class


class db_triggerlog(renderer_class):
    """ Default Renderer - Basic Output for Any XML File """

    _namespace_uri = "http://thermal.cnde.iastate.edu/triggerlog"
    _namespace_local = "triggerlog"
    _default_content_mode = "full"
    _default_style_mode = "view_log_data"
    _default_recursion_depth = 2

    def getContent(self):
        if self._content_mode != "raw" and self._caller == "databrowse" and "ajax" not in self._web_support.req.form:
            f = open(self._fullpath, 'r')
            xml = etree.parse(f)
            f.close()
            return xml.getroot()
        elif self._content_mode != "raw" and self._caller == "db_triggerlog_database" and self._style_mode == 'view_trigger_log':
            f = open(self._fullpath, 'r')
            xml = etree.parse(f)
            f.close()
            return xml.getroot()
        elif self._content_mode == "raw":
            raise self.RendererException("Raw Mode is Not Supported by this Plugin")
        else:
            return None
        pass

    pass
