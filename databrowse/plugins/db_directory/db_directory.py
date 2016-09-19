#!/usr/bin/env python
###############################################################################
## Databrowse:  An Extensible Data Management Platform                       ##
## Copyright (C) 2012-2016 Iowa State University Research Foundation, Inc.   ##
## All rights reserved.                                                      ##
##                                                                           ##
## Redistribution and use in source and binary forms, with or without        ##
## modification, are permitted provided that the following conditions are    ##
## met:                                                                      ##
##   1. Redistributions of source code must retain the above copyright       ##
##      notice, this list of conditions and the following disclaimer.        ##
##   2. Redistributions in binary form must reproduce the above copyright    ##
##      notice, this list of conditions and the following disclaimer in the  ##
##      documentation and/or other materials provided with the distribution. ##
##   3. Neither the name of the copyright holder nor the names of its        ##
##      contributors may be used to endorse or promote products derived from ##
##      this software without specific prior written permission.             ##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS       ##
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED ##
## TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A           ##
## PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER ##
## OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,  ##
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,       ##
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR        ##
## PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF    ##
## LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING      ## 
## NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS        ##
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.              ##
##                                                                           ##
## This material is based on work supported by the Air Force Research        ##
## Laboratory under Contract #FA8650-10-D-5210, Task Order #023 and          ##
## performed at Iowa State University.                                       ##
##                                                                           ##
## DISTRIBUTION A.  Approved for public release:  distribution unlimited;    ##
## 19 Aug 2016; 88ABW-2016-4051.											 ##
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

    def recursiveloop(self, dirname, chxlist):
        chxdirlist = self.getDirectoryList(os.path.abspath(self._web_support.dataroot + '/' + self._web_support.checklistpath + '/' + dirname))
        for item in chxdirlist:
            if item.endswith(".chx"):
                itemurl = self.getURL(os.path.normpath(self._web_support.checklistpath + '/' + dirname + '/' + item), handler=None)
                etree.SubElement(chxlist, '{%s}chxfile' % (self._namespace_uri), nsmap=self.nsmap, url=itemurl, name=item)
                pass
            if os.path.isdir(os.path.abspath(self._web_support.dataroot + '/' + self._web_support.checklistpath + '/' + dirname + '/' + item)):
                if len([x for x in self.getDirectoryList(os.path.abspath(self._web_support.dataroot + '/' + self._web_support.checklistpath + '/' + os.path.normpath(dirname + '/' + item))) if (x.endswith('.chx') or os.path.isdir(os.path.abspath(self._web_support.dataroot + '/' + self._web_support.checklistpath + '/' + os.path.normpath(dirname + '/' + item + '/' + x))))]) > 0:
                    subchxlist = etree.SubElement(chxlist, '{%s}chxdir' % (self._namespace_uri), nsmap=self.nsmap, url=self.getURL(os.path.normpath(self._web_support.checklistpath + '/'  + dirname + '/' + item), handler=None), name=item)
                    self.recursiveloop(os.path.normpath(dirname + '/' + item), subchxlist)
                pass

    def __init__(self, relpath, fullpath, web_support, handler_support, caller, handlers, content_mode=_default_content_mode, style_mode=_default_style_mode, recursion_depth=_default_recursion_depth):
        """ Load all of the values provided by initialization """
        super(db_directory, self).__init__(relpath, fullpath, web_support, handler_support, caller, handlers, content_mode, style_mode)
        if caller == "databrowse":
            uphref = self.getURLToParent(self._relpath)
            xmlroot = etree.Element('{%s}dir' % self._namespace_uri, nsmap=self.nsmap, path=self._fullpath, relpath=self._relpath, dataroot=self._web_support.dataroot, uphref=uphref, resurl=self._web_support.resurl, siteurl=self._web_support.siteurl, root="True")
            topmenu = etree.Element('{http://thermal.cnde.iastate.edu/databrowse}navbar', nsmap=self.nsmap, xmlns="http://www.w3.org/1999/xhtml")
            navelem = etree.SubElement(topmenu, "{http://thermal.cnde.iastate.edu/databrowse}navelem", nsmap=self.nsmap)
            title = etree.SubElement(navelem, "{http://www.w3.org/1999/xhtml}a", nsmap=self.nsmap)
            title.text = "View Options"
            navitems = etree.SubElement(navelem, "{http://thermal.cnde.iastate.edu/databrowse}navdir", alwaysopen="true", nsmap=self.nsmap)
            if not "showhiddenfiles" in self._web_support.req.form:
                menuitem = etree.SubElement(navitems, '{http://thermal.cnde.iastate.edu/databrowse}navelem', nsmap=self.nsmap)
                menulink = etree.SubElement(menuitem, '{http://www.w3.org/1999/xhtml}a', href=self.getURL(self._relpath, showhiddenfiles=""), nsmap=self.nsmap)
                menulink.text = "Show Hidden Files"
            else:
                menuitem = etree.SubElement(navitems, '{http://thermal.cnde.iastate.edu/databrowse}navelem', nsmap=self.nsmap)
                menulink = etree.SubElement(menuitem, '{http://www.w3.org/1999/xhtml}a', href=self.getURL(self._relpath, showhiddenfiles=None), nsmap=self.nsmap)
                menulink.text = "Hide Hidden Files"
            self._web_support.menu.AddMenu(topmenu)
            pass
        else:
            link = self.getURL(self._relpath, handler=None)
            xmlroot = etree.Element('{%s}dir' % self._namespace_uri, nsmap=self.nsmap, name=os.path.basename(self._relpath), path=self._fullpath, relpath=self._relpath, dataroot=self._web_support.dataroot, href=link, resurl=self._web_support.resurl)
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
                if handler in self._handler_support.directoryplugins:
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
                if content is not None and content.tag.startswith("{%s}" % self._namespace_uri):
                    content.set('icon', icon)
                    content.set('overlay', overlay)
                    xmlroot.append(content)
                else:
                    xmlchild = etree.SubElement(xmlroot, '{%s}file' % (self._namespace_uri), nsmap=self.nsmap, fullpath=itemfullpath, relpath=itemrelpath, basename=os.path.basename(itemfullpath), link=self.getURL(itemrelpath, handler=None), icon=icon, overlay=overlay)
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
            chxlist = etree.SubElement(xmlroot, '{%s}chxlist' % (self._namespace_uri), nsmap=self.nsmap)
            #chxdirlist = self.getDirectoryList(os.path.abspath(self._web_support.dataroot + '/' + self._web_support.checklistpath))

            

            self.recursiveloop('/', chxlist)

            #for item in [item for item in chxdirlist if item.endswith(".chx")]:
            #    itemurl = self.getURL(os.path.join(self._web_support.checklistpath, item), handler=None)
            #    etree.SubElement(chxlist, '{%s}chxfile' % (self._namespace_uri), nsmap=self.nsmap, url=itemurl, name=item)
            #    pass
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
