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
""" plugins/renderers/dbr_wsgi_generic.py - Default Handler for WSGI Scripts """

import imp
import os
import os.path
import copy
from lxml import etree
from renderer_support import renderer_class


class dbr_wsgi_generic(renderer_class):
    """ Default Renderer for WSGI Scripts - Simply Passes Everything Off To The Script """

    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/wsgigeneric"
    _namespace_local = "wsgigeneric"
    _default_content_mode = "raw"
    _default_style_mode = "list"
    _default_recursion_depth = 2

    def getContent(self):
        if self._content_mode is "summary" or self._content_mode is "detailed" or self._content_mode is "title":
            link = self.getURL(self._relpath)
            xmlroot = etree.Element('{%s}wsgigeneric' % self._namespace_uri, name=os.path.basename(self._relpath), href=link)
            return xmlroot
        elif self._content_mode is "raw":
            savedCWD = os.getcwd()
            tempCWD = os.path.dirname(self._fullpath)
            os.chdir(tempCWD)
            modulename = os.path.splitext(os.path.basename(self._fullpath))[0]
            module = imp.load_source(modulename, self._fullpath)
            environcopy = copy.copy(self._web_support.req.environ)
            environcopy['DATABROWSE_FILENAME'] = environcopy['SCRIPT_FILENAME']
            environcopy['SCRIPT_FILENAME'] = self._fullpath
            output = module.application(environcopy, self._web_support.req.start_response)
            os.chdir(savedCWD)
            self._web_support.req.output_done = True
            return output
        else:
            raise self.RendererException("Invalid Content Mode")

    pass
