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
""" plugins/renderers/db_html_generic.py - Generic HTML Files """

import os
import os.path
from lxml import etree
from databrowse.support.renderer_support import renderer_class


class db_webpage_viewer(renderer_class):
    """ Generic HTML Files """

    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/dbhtml"
    _namespace_local = "dbhtml"
    _default_content_mode = "full"
    _default_style_mode = "view_webpage"
    _default_recursion_depth = 2

    def getContent(self):
        if self._caller != "databrowse":
            return None
        else:
            if self._content_mode is "full":
                xmlroot = etree.Element('{%s}dbhtml' % self._namespace_uri, name=os.path.basename(self._relpath), resurl=self._web_support.resurl)
                if self.getSize() > 0:
                    f = open(self._fullpath, 'r')
                    parser = etree.HTMLParser()
                    htmltree = etree.parse(f, parser)
                    f.close()
                    htmlroot = htmltree.getroot()
                    xmlchild = etree.SubElement(xmlroot, "contents")
                    xmlchild.append(htmlroot)
                    pass
                return xmlroot
            else:
                raise self.RendererException("Invalid Content Mode")

    pass
