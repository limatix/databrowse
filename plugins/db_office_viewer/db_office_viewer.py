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
""" plugins/renderers/db_office_viewer.py - Default Office Document Viewer """

import os
import os.path
import time
import pwd
import grp
from stat import *
from lxml import etree
from renderer_support import renderer_class
import magic
import subprocess


class db_office_viewer(renderer_class):
    """ Default Renderer - Basic Output for Any File """

    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/office"
    _namespace_local = "office"
    _default_content_mode = "full"
    _default_style_mode = "preview_office_document"
    _default_recursion_depth = 2

    def getContent(self):
        if self._content_mode == "full":
            try:
                st = os.stat(self._fullpath)
            except IOError:
                return "Failed To Get File Information: %s" % (self._fullpath)
            else:
                file_size = st[ST_SIZE]
                file_mtime = time.asctime(time.localtime(st[ST_MTIME]))
                file_ctime = time.asctime(time.localtime(st[ST_CTIME]))
                file_atime = time.asctime(time.localtime(st[ST_ATIME]))

                viewlink = self.getURL(self._relpath, content_mode="raw", pdf="pdf")
                pdflink = self.getURL(self._relpath, content_mode="raw", pdf="pdf", download="download")
                downlink = self.getURL(self._relpath, content_mode="raw")

                xmlroot = etree.Element('{%s}office' % self._namespace_uri, name=os.path.basename(self._relpath), viewlink=viewlink, pdflink=pdflink, resurl=self._web_support.resurl, downlink=downlink)

                xmlchild = etree.SubElement(xmlroot, "filename")
                xmlchild.text = os.path.basename(self._fullpath)

                xmlchild = etree.SubElement(xmlroot, "path")
                xmlchild.text = os.path.dirname(self._fullpath)

                xmlchild = etree.SubElement(xmlroot, "filesize")
                xmlchild.text = self.ConvertUserFriendlySize(file_size)

                xmlchild = etree.SubElement(xmlroot, "mtime")
                xmlchild.text = file_mtime

                xmlchild = etree.SubElement(xmlroot, "ctime")
                xmlchild.text = file_ctime

                xmlchild = etree.SubElement(xmlroot, "atime")
                xmlchild.text = file_atime

                # File Permissions
                xmlchild = etree.SubElement(xmlroot, "permissions")
                xmlchild.text = self.ConvertUserFriendlyPermissions(st[ST_MODE])

                # User and Group
                username = pwd.getpwuid(st[ST_UID])[0]
                groupname = grp.getgrgid(st[ST_GID])[0]
                xmlchild = etree.SubElement(xmlroot, "owner")
                xmlchild.text = "%s:%s" % (username, groupname)

                magicstore = magic.open(magic.MAGIC_MIME)
                magicstore.load()
                contenttype = magicstore.file(self._fullpath)
                xmlchild = etree.SubElement(xmlroot, "contenttype")
                xmlchild.text = contenttype

                return xmlroot
        elif self._content_mode == "summary" or self._content_mode == "title":
            return None
        elif self._content_mode == "raw":
            if "pdf" in self._web_support.req.form:
                if self.CacheFileExists(None, 'pdf'):
                    size = os.path.getsize(self.getCacheFileName(None, 'pdf'))
                    f = self.getCacheFileHandler('rb', None, 'pdf')
                    if "download" in self._web_support.req.form:
                        self._web_support.req.response_headers['Content-Disposition'] = "attachment; filename=" + os.path.basename(self.getCacheFileName(None, 'pdf'))
                    self._web_support.req.response_headers['Content-Type'] = 'application/pdf'
                    self._web_support.req.response_headers['Content-Length'] = str(size)
                    self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                    self._web_support.req.output_done = True
                    if 'wsgi.file_wrapper' in self._web_support.req.environ:
                        return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
                    else:
                        return iter(lambda: f.read(1024))
                else:
                    self.PrepareCacheDir()
                    os.environ["HOME"] = "/home/www"
                    subprocess.call(["/usr/bin/soffice", "--headless", "--convert-to", "pdf", "--outdir", self.getCacheDirName(), self._fullpath])
                    try:
                        size = os.path.getsize(self.getCacheFileName(None, 'pdf'))
                        f = self.getCacheFileHandler('rb', None, 'pdf')
                        if "download" in self._web_support.req.form:
                            self._web_support.req.response_headers['Content-Disposition'] = "attachment; filename=" + os.path.basename(self.getCacheFileName(None, 'pdf'))
                        self._web_support.req.response_headers['Content-Type'] = 'application/pdf'
                        self._web_support.req.response_headers['Content-Length'] = str(size)
                        self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                        self._web_support.req.output_done = True
                        if 'wsgi.file_wrapper' in self._web_support.req.environ:
                            return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
                        else:
                            return iter(lambda: f.read(1024))
                    except Exception as err:
                        raise self.RendererException("Unable to Generate PDF File - Check File Permissions")
            else:
                magicstore = magic.open(magic.MAGIC_MIME)
                magicstore.load()
                contenttype = magicstore.file(self._fullpath)
                size = os.path.getsize(self._fullpath)
                self._web_support.req.response_headers['Content-Type'] = contenttype
                self._web_support.req.response_headers['Content-Length'] = str(size)
                f = open(self._fullpath, "rb")
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
