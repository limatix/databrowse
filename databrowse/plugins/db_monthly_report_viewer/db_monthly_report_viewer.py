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
""" plugins/renderers/db_xml_monthly_rpt.py - Monthly Report XML Files """

import os
import os.path
from lxml import etree
from renderer_support import renderer_class


class db_monthly_report_viewer(renderer_class):
    """ Monthly Report XML Files """

    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/monthlyrptxml"
    _namespace_local = "monthlyrptxml"
    _default_content_mode = "full"
    _default_style_mode = "view_report"
    _default_recursion_depth = 2

    def getContent(self):
        if self._caller != "databrowse":
            return None
        else:
            if self._content_mode is "full":
                f = open(self._fullpath, 'r')
                xmltree = etree.parse(f)
                f.close()
                g = open(os.path.dirname(self._fullpath) + '/view_monthly_reports.xml', 'r')
                xsltransform = etree.parse(g)
                g.close()
                transformedxml = xmltree.xslt(xsltransform)
                xmloutput = etree.XML(str(transformedxml))
                return xmloutput
            else:
                raise self.RendererException("Invalid Content Mode")

    pass
