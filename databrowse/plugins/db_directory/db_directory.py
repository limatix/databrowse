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
""" plugins/renderers/db_directory.py - Basic Output for Any Folder """

import os
import os.path
from lxml import etree
from databrowse.support.renderer_support import renderer_class


class db_directory(renderer_class):
    """ Default Folder Renderer - Basic Output for Any Folder """

    _xml = None
    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/dir"
    _namespace_local = "dir"
    _default_content_mode = "title"
    _default_style_mode = "list"
    _default_recursion_depth = 1

    def __init__(self, relpath, fullpath, web_support, handler_support, caller, handlers, content_mode=_default_content_mode, style_mode=_default_style_mode, recursion_depth=_default_recursion_depth):
        """ Load all of the values provided by initialization """
        super(db_directory, self).__init__(relpath, fullpath, web_support, handler_support, caller, handlers, content_mode, style_mode)
        if caller == "databrowse":
            uphref = self.getURLToParent(self._relpath)
            xmlroot = etree.Element('{%s}dir' % self._namespace_uri, path=self._fullpath, relpath=self._relpath, dataroot=self._web_support.dataroot, uphref=uphref, resurl=self._web_support.resurl, siteurl=self._web_support.siteurl, root="True")
            topmenu = etree.Element('{http://thermal.cnde.iastate.edu/databrowse}navbar', xmlns="http://www.w3.org/1999/xhtml")
            navelem = etree.SubElement(topmenu, "{http://thermal.cnde.iastate.edu/databrowse}navelem")
            title = etree.SubElement(navelem, "{http://www.w3.org/1999/xhtml}a")
            title.text = "View Options"
            navitems = etree.SubElement(navelem, "{http://thermal.cnde.iastate.edu/databrowse}navdir", alwaysopen="true")
            if not "showhiddenfiles" in self._web_support.req.form:
                menuitem = etree.SubElement(navitems, '{http://thermal.cnde.iastate.edu/databrowse}navelem')
                menulink = etree.SubElement(menuitem, '{http://www.w3.org/1999/xhtml}a', href=self.getURL(self._relpath, showhiddenfiles=""))
                menulink.text = "Show Hidden Files"
            else:
                menuitem = etree.SubElement(navitems, '{http://thermal.cnde.iastate.edu/databrowse}navelem')
                menulink = etree.SubElement(menuitem, '{http://www.w3.org/1999/xhtml}a', href=self.getURL(self._relpath, showhiddenfiles=None))
                menulink.text = "Hide Hidden Files"
            self._web_support.menu.AddMenu(topmenu)
            pass
        else:
            link = self.getURL(self._relpath)
            xmlroot = etree.Element('{%s}dir' % self._namespace_uri, name=os.path.basename(self._relpath), path=self._fullpath, relpath=self._relpath, dataroot=self._web_support.dataroot, href=link, resurl=self._web_support.resurl)
            pass
        if "ajax" in self._web_support.req.form:
            xmlroot.set("ajaxreq", "True")
            pass
        if recursion_depth != 0:
            caller = self.__class__.__name__
            dirlist = self.getDirectoryList(self._fullpath)
            for item in dirlist:
                itemrelpath = os.path.join(self._relpath, item)
                itemfullpath = os.path.join(self._fullpath, item)
                (handlers, icon) = self._handler_support.GetHandlerAndIcon(itemfullpath)
                handler = handlers[-1]
                if handler in self._handler_support.directoryplugins:
                    icon = self._handler_support.directoryplugins[handler]
                if handler == "db_directory":
                    renderer = self.__class__(itemrelpath, itemfullpath, self._web_support, self._handler_support, caller, handlers, content_mode=content_mode, style_mode=style_mode, recursion_depth=recursion_depth-1)
                else:
                    exec "import databrowse.plugins.%s.%s as %s_module" % (handler, handler, handler)
                    exec "renderer = %s_module.%s(itemrelpath, itemfullpath, self._web_support, self._handler_support, caller, handlers, content_mode='%s', style_mode='%s', recursion_depth=%i)" % (handler, handler, content_mode, style_mode, recursion_depth - 1)
                content = renderer.getContent()
                if os.path.islink(itemfullpath):
                    overlay = "link"
                elif not os.access(itemfullpath, os.W_OK):
                    overlay = "readonly"
                elif not os.access(itemfullpath, os.R_OK):
                    overlay = "unreadable"
                else:
                    overlay = "none"
                xmlchild = etree.SubElement(xmlroot, '{%s}file' % (self._namespace_uri), fullpath=itemfullpath, relpath=itemrelpath, basename=os.path.basename(itemfullpath), link=self.getURL(itemrelpath, handler=None), icon=icon, overlay=overlay)
                if content is not None:
                    xmlchild.append(content)
                    pass
                pass
            pass
        else:
            #ajax url and what not
            xmlroot.set("ajax", "True")
            xmlroot.set("ajaxurl", self.getURL(self._relpath, recursion_depth=1, nopagestyle=True, content_mode=self._content_mode, style_mode=self._style_mode))
            pass
        if self._caller == "databrowse" and self._web_support.checklistpath is not None:
            chxlist = etree.SubElement(xmlroot, '{%s}chxlist' % (self._namespace_uri))
            chxdirlist = self.getDirectoryList(os.path.abspath(self._web_support.dataroot + '/' + self._web_support.checklistpath))
            for item in [item for item in chxdirlist if item.endswith(".chx")]:
                itemurl = self.getURL(os.path.join(self._web_support.checklistpath, item), handler=None)
                etree.SubElement(chxlist, '{%s}chxfile' % (self._namespace_uri), url=itemurl, name=item)
                pass
            pass
        self._xml = xmlroot
        pass

    def getContent(self):
        if self._content_mode == "detailed" or self._content_mode == "summary" or self._content_mode == "title":
            return self._xml
        else:
            raise self.RendererException("Invalid Content Mode")
        pass

pass
