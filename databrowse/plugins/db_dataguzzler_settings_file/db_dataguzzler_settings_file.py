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
""" plugins/renderers/db_default.py - Default Renderer - Basic Output for Any File """

import os
import os.path
import time
import pwd
import grp
from stat import *
from lxml import etree
from databrowse.support.renderer_support import renderer_class
import magic


class db_dataguzzler_settings_file(renderer_class):
    """ Default Renderer - Basic Output for Any File """

    _namespace_uri = "http://thermal.cnde.iastate.edu/dgset"
    _namespace_local = "dgset"
    _default_content_mode = "full"
    _default_style_mode = "settings_preview"
    _default_recursion_depth = 2

    def getContent(self):
        if self._caller != "databrowse":
            return None
        else:
            if self._content_mode == "full":
                icon = self._handler_support.GetIcon('application/x-dataguzzler-settings', 'set')
                name = os.path.basename(self._relpath) if self._relpath != '/' else os.path.basename(self._fullpath)
                downlink = self.getURL(self._relpath, content_mode="raw", download="true")
                xmlroot = etree.Element('{%s}dgset' % self._namespace_uri, name=name, downlink=downlink, icon=icon)

                f = open(self._fullpath, 'rb')
                rawcontents = f.read()
                contents = rawcontents.split("\r\n")[1]
                contents = contents.split(";")
                for item in contents:
                    xmlchild = etree.SubElement(xmlroot, 'setting')
                    name = etree.SubElement(xmlchild, 'name')
                    name.text = item.split(" ")[0]
                    value = etree.SubElement(xmlchild, 'value')
                    value.text = " ".join(item.split(" ")[1:])

                return xmlroot
            elif self._content_mode == "raw":
                size = os.path.getsize(self._fullpath)
                magicstore = magic.open(magic.MAGIC_MIME)
                magicstore.load()
                contenttype = magicstore.file(self._fullpath)
                f = open(self._fullpath, "rb")
                if "ContentType" in self._web_support.req.form:
                    self._web_support.req.response_headers['Content-Type'] = self._web_support.req.form["ContentType"].value
                else:
                    self._web_support.req.response_headers['Content-Type'] = contenttype
                self._web_support.req.response_headers['Content-Length'] = str(size)
                if "download" in self._web_support.req.form:
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
