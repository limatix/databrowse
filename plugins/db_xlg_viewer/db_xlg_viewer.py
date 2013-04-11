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
""" plugins/renderers/dbr_xlg_viewer.py - Experiment Log Viewer """

import os
import os.path
import time
import pwd
import grp
from stat import *
from lxml import etree
from renderer_support import renderer_class
import magic


class dbr_xlg_viewer(renderer_class):
    """ Experiment Log Viewer """

    _namespace_uri = "http://thermal.cnde.iastate.edu/datacollect"
    _namespace_local = "dc"
    _default_content_mode = "detailed"
    _default_style_mode = "list"
    _default_recursion_depth = 2

    def getContent(self):
        if self._content_mode == "detailed":
            # Contents of File
            f = open(self._fullpath)
            xmlroot = etree.XML(f.read())
            f.close()

            return xmlroot
        elif self._content_mode == "summary" or self._content_mode == "title":
            link = self.getURL(self._relpath)
            xmlroot = etree.Element('{%s}experiment' % self._namespace_uri, name=os.path.basename(self._relpath), href=link)
            return xmlroot
        elif self._content_mode == "raw":
            size = os.path.getsize(self._fullpath)
            magicstore = magic.open(magic.MAGIC_MIME)
            magicstore.load()
            contenttype = magicstore.file(self._fullpath)
            f = open(self._fullpath, "rb")
            self._web_support.req.response_headers['Content-Type'] = contenttype
            self._web_support.req.response_headers['Content-Length'] = str(size)
            self._web_support.req.response_headers['Content-Disposition'] = "attachment; filename=" + os.path.basename(self._fullpath)
            self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
            self._web_support.req.output_done = True
            if 'wsgi.file_wrapper' in self._web_support.req.environ:
                return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
            else:
                return iter(lambda: f.read(1024))
        else:
            raise self.RendererException("Invalid Content Mode")
        pass

    pass
