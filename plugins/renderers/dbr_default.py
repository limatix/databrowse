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
""" plugins/renderers/dbr_default.py - Default Renderer - Basic Output for Any File """

import os
import os.path
import time
from stat import *
from lxml import etree
from renderer_support import renderer_class
import magic


class dbr_default(renderer_class):
    """ Default Renderer - Basic Output for Any File """

    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/default"
    _namespace_local = "default"

    def __init__(self, relpath, fullpath, web_support, handler_support, caller, content_mode="detailed", style_mode="list", recursion_depth=2):
        """ Load all of the values provided by initialization """
        super(dbr_default, self).__init__(relpath, fullpath, web_support, handler_support, caller, content_mode, style_mode)
        etree.register_namespace("default", "http://thermal.cnde.iastate.edu/databrowse/default")
        pass

    def getContent(self):
        if self._content_mode == "detailed":
            try:
                st = os.stat(self._fullpath)
            except IOError:
                return "Failed To Get File Information: %s" % (self._fullpath)
            else:
                file_size = st[ST_SIZE]
                file_mtime = time.asctime(time.localtime(st[ST_MTIME]))
                file_ctime = time.asctime(time.localtime(st[ST_CTIME]))
                file_atime = time.asctime(time.localtime(st[ST_ATIME]))

                xmlroot = etree.Element('{http://thermal.cnde.iastate.edu/databrowse/default}default')

                xmlchild = etree.SubElement(xmlroot, "filename")
                xmlchild.text = os.path.basename(self._fullpath)

                xmlchild = etree.SubElement(xmlroot, "path")
                xmlchild.text = os.path.dirname(self._fullpath)

                xmlchild = etree.SubElement(xmlroot, "size")
                xmlchild.text = str(file_size)

                xmlchild = etree.SubElement(xmlroot, "mtime")
                xmlchild.text = file_mtime

                xmlchild = etree.SubElement(xmlroot, "ctime")
                xmlchild.text = file_ctime

                xmlchild = etree.SubElement(xmlroot, "atime")
                xmlchild.text = file_atime

                self.loadStyle()

                return xmlroot
        elif self._content_mode == "summary" or self._content_mode == "title":
            self.loadStyle()
            link = self._web_support.siteurl + self._relpath
            xmlroot = etree.Element('{http://thermal.cnde.iastate.edu/databrowse/default}default', xmlns="http://thermal.cnde.iastate.edu/databrowse/default", name=os.path.basename(self._relpath), href=link)
            return xmlroot
        elif self._content_mode == "raw":
            size = os.path.getsize(self._fullpath)
            if hasattr(magic, "Magic"):
                # new python-magic API
                mime = magic.Magic(mime=True)
                contenttype = mime.from_file(self._fullpath)
                pass
            else:
                magicstore = magic.open(magic.MAGIC_NONE)
                magicstore.load()
                contenttype = magicstore.file(self._fullpath)
                pass
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
            raise self.RendererException(1102)
        pass

    pass
