#!/usr/bin/env python
###############################################################################
## Databrowse:  An Extensible Data Management Platform                       ##
## Copyright (C) 2012 Iowa State University                                  ##
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
""" plugins/renderers/dbr_xml_monthly_rpt.py - Monthly Report XML Files """

import os
import os.path
from lxml import etree
from renderer_support import renderer_class


class dbr_xml_monthly_rpt(renderer_class):
    """ Monthly Report XML Files """

    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/monthlyrptxml"
    _namespace_local = "monthlyrptxml"
    _default_content_mode = "full"
    _default_style_mode = "full"
    _default_recursion_depth = 2

    def getContent(self):
        if self._content_mode is "summary" or self._content_mode is "detailed" or self._content_mode is "title":
            link = self.getURL(self._relpath)
            xmlroot = etree.Element('{%s}monthlyrptxml' % self._namespace_uri, name=os.path.basename(self._relpath), href=link)
            return xmlroot
        elif self._content_mode is "full":
            class FileResolver(etree.Resolver):
                def resolve(self, url, pubid, context):
                    return self.resolve_filename(url, context)

            parser = etree.XMLParser()
            parser.resolvers.add(FileResolver())
            f = open(self._fullpath, 'r')
            xmltree = etree.parse(f, parser)
            f.close()
            return xmltree.getroot()
        else:
            raise self.RendererException("Invalid Content Mode")

    pass
