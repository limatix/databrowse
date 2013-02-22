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
from lxml import etree
from renderer_support import renderer_class


class dbr_wsgi_generic(renderer_class):
    """ Default Renderer for WSGI Scripts - Simply Passes Everything Off To The Script """

    _savedCWD = None
    _tempCWD = None
    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/wsgigeneric"
    _namespace_local = "wsgigeneric"

    def __init__(self, relpath, fullpath, web_support, handler_support, caller, content_mode="raw", style_mode="list", recursion_depth=2):
        """ Load all of the values provided by initialization """
        super(dbr_wsgi_generic, self).__init__(relpath, fullpath, web_support, handler_support, caller, content_mode, style_mode)
        self._savedCWD = os.getcwd()
        self._tempCWD = os.path.dirname(self._fullpath)
        etree.register_namespace("wsgigeneric", "http://thermal.cnde.iastate.edu/databrowse/wsgigeneric")
        pass

    def getContent(self):
        if self._content_mode is "summary" or self._content_mode is "detailed" or self._content_mode is "title":
            self.loadStyle()
            link = self.getURL(self._relpath)
            xmlroot = etree.Element('{http://thermal.cnde.iastate.edu/databrowse/wsgigeneric}wsgigeneric', xmlns="http://thermal.cnde.iastate.edu/databrowse/wsgigeneric", name=os.path.basename(self._relpath), href=link)
            return xmlroot
        elif self._content_mode is "raw":
            os.chdir(self._tempCWD)
            modulename = os.path.splitext(os.path.basename(self._fullpath))[0]
            module = imp.load_source(modulename, self._fullpath)
            output = module.application(self._web_support.req.environ, self._web_support.req.start_response)
            os.chdir(self._savedCWD)
            self._web_support.req.output_done = True
            #return output
            return output
        else:
            raise self.RendererException(1102)

    pass
