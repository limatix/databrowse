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
""" plugins/renderers/db_wsgi_monthly_rpt.py - Hanlder for Monthly Reports """

import imp
import os
import os.path
import copy
from lxml import etree
from renderer_support import renderer_class


class db_monthly_report_tool(renderer_class):
    """ Default Renderer for WSGI Scripts - Simply Passes Everything Off To The Script """

    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/monthrpt"
    _namespace_local = "monthrpt"
    _default_content_mode = "full"
    _default_style_mode = "complete_monthly_report"
    _default_recursion_depth = 2

    def dummy_start_response(self, status, headers, exc_info=None):
        self._web_support.req.status = status
        for item in headers:
            self._web_support.req.response_headers[item[0]] = item[1]
            pass
        self._web_support.req.response_headers['Content-Type'] = 'text/html'
        pass

    def getContent(self):
        if self._caller != "databrowse":
            return None
        else:
            if self._content_mode is "full":
                savedCWD = os.getcwd()
                tempCWD = os.path.dirname(self._fullpath)
                os.chdir(tempCWD)
                modulename = os.path.splitext(os.path.basename(self._fullpath))[0]
                module = imp.load_source(modulename, self._fullpath)
                environcopy = copy.copy(self._web_support.req.environ)
                environcopy['DATABROWSE_FILENAME'] = environcopy['SCRIPT_FILENAME']
                environcopy['SCRIPT_FILENAME'] = self._fullpath
                etree.register_namespace("monthlyrpt", "http://thermal.cnde.iastate.edu/monthly_rpt")
                output = module.application(environcopy, self.dummy_start_response)
                os.chdir(savedCWD)
                del module
                del environcopy
                return etree.XML(output)
            elif self._content_mode is "raw":
                savedCWD = os.getcwd()
                tempCWD = os.path.dirname(self._fullpath)
                os.chdir(tempCWD)
                modulename = os.path.splitext(os.path.basename(self._fullpath))[0]
                module = imp.load_source(modulename, self._fullpath)
                environcopy = copy.copy(self._web_support.req.environ)
                environcopy['DATABROWSE_FILENAME'] = environcopy['SCRIPT_FILENAME']
                environcopy['SCRIPT_FILENAME'] = self._fullpath
                etree.register_namespace("monthlyrpt", "http://thermal.cnde.iastate.edu/monthly_rpt")
                output = module.application(environcopy, self._web_support.req.start_response)
                os.chdir(savedCWD)
                self._web_support.req.output_done = True
                del module
                del environcopy
                return output
            else:
                raise self.RendererException("Invalid Content Mode")

    pass
