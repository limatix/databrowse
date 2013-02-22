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
""" plugins/renderers/dbr_directory_generic.py - Basic Output for Any Folder """

import os
import os.path
from lxml import etree
from renderer_support import renderer_class


class dbr_directory_generic(renderer_class):
    """ Default Folder Renderer - Basic Output for Any Folder """

    _detailed_xml = None
    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/dir"
    _namespace_local = "dir"

    def __init__(self, relpath, fullpath, web_support, handler_support, caller, content_mode="title", style_mode="list", recursion_depth=2):
        """ Load all of the values provided by initialization """
        super(dbr_directory_generic, self).__init__(relpath, fullpath, web_support, handler_support, caller, content_mode, style_mode)
        etree.register_namespace("dir", "http://thermal.cnde.iastate.edu/databrowse/dir")
        #if content_mode is "detailed":
        dirlist = os.listdir(self._fullpath)
        if caller == "databrowse":
            uphref = self.getURLToParent(self._relpath)
            xmlroot = etree.Element('{http://thermal.cnde.iastate.edu/databrowse/dir}dir', path=self._fullpath, uphref=uphref, resurl=self._web_support.resurl, root="True")
            pass
        else:
            link = self.getURL(self._relpath)
            xmlroot = etree.Element('{http://thermal.cnde.iastate.edu/databrowse/dir}dir', name=os.path.basename(self._relpath), path=self._fullpath, href=link, resurl=self._web_support.resurl)
            pass
        style = {}
        if recursion_depth is not 0:
            for item in dirlist:
                itemrelpath = os.path.join(self._relpath, item)
                itemfullpath = os.path.join(self._fullpath, item)
                handler = self._handler_support.GetHandler(itemfullpath)
                print "--- Preparing to Load Handler %s ---" % handler
                exec "import %s as %s_module" % (handler, handler)
                exec "renderer = %s_module.%s(itemrelpath, itemfullpath, self._web_support, self._handler_support, caller='dbr_directory_generic', content_mode='%s', style_mode='%s', recursion_depth=%i)" % (handler, handler, content_mode, style_mode, recursion_depth - 1)
                content = renderer.getContent()
                xmlchild = etree.SubElement(xmlroot, "{http://thermal.cnde.iastate.edu/databrowse/dir}file", fullpath=itemfullpath, relpath=itemrelpath)
                xmlchild.append(content)
                pass
            pass
        self._detailed_xml = xmlroot
        pass

    def getContent(self):
        self.loadStyle()
        if self._content_mode == "detailed" or self._content_mode == "summary" or self._content_mode == "title":
            return self._detailed_xml
        else:
            raise self.RendererException(1102)
        pass

pass
