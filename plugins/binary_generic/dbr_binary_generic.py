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
""" plugins/renderers/dbr_binary_generic.py - Default Binary Renderer """

import os
import os.path
import time
import pwd
import grp
from stat import *
from lxml import etree
from renderer_support import renderer_class
import magic


class dbr_binary_generic(renderer_class):
    """ Default Renderer - Basic Output for Any Binary File """

    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/binary"
    _namespace_local = "binary"
    _default_content_mode = "detailed"
    _default_style_mode = "list"
    _default_recursion_depth = 2

    def streamGenerator(self):
        if "offset" not in self._web_support.req.form:
            offset = 0
            pass
        else:
            offset = int(self._web_support.req.form['offset'].value)
            pass
        if "lines" not in self._web_support.req.form:
            lines = 20
            pass
        else:
            lines = int(self._web_support.req.form['lines'].value)
            pass
        self._web_support.req.response_headers['Content-Type'] = 'text/plain'
        self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
        self._web_support.req.output_done = True
        f = open(self._fullpath, 'rb')
        myfilter = ''.join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)])
        myhex = lambda data: ' '.join("%02x" % ord(i) for i in data)
        mystr = lambda data: ''.join(["%s" % ((ord(x) <= 127 and myfilter[ord(x)]) or '.') for x in data])
        if offset is not 0:
            f.seek(offset)
            pass
        for line in range(offset, os.path.getsize(self._fullpath), 16)[:lines]:
            data = f.read(16)
            yield '{0:08x} | {1:47} | {2}\n'.format(line, myhex(data), mystr(data))
        f.close()

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
                magicstore = magic.open(magic.MAGIC_MIME)
                magicstore.load()
                contenttype = magicstore.file(self._fullpath)
                extension = os.path.splitext(self._fullpath)[1][1:]
                icon = self._handler_support.GetIcon(contenttype, extension)

                downlink = self.getURL(self._relpath, content_mode="raw", download="true")

                xmlroot = etree.Element('{%s}binary' % self._namespace_uri, name=os.path.basename(self._relpath), resurl=self._web_support.resurl, downlink=downlink, icon=icon)

                xmlchild = etree.SubElement(xmlroot, "filename")
                xmlchild.text = os.path.basename(self._fullpath)

                xmlchild = etree.SubElement(xmlroot, "path")
                xmlchild.text = os.path.dirname(self._fullpath)

                xmlchild = etree.SubElement(xmlroot, "size")
                xmlchild.text = self.ConvertUserFriendlySize(file_size)

                xmlchild = etree.SubElement(xmlroot, "mtime")
                xmlchild.text = file_mtime

                xmlchild = etree.SubElement(xmlroot, "ctime")
                xmlchild.text = file_ctime

                xmlchild = etree.SubElement(xmlroot, "atime")
                xmlchild.text = file_atime

                # Content Type
                xmlchild = etree.SubElement(xmlroot, "contenttype")
                xmlchild.text = contenttype

                # File Permissions
                xmlchild = etree.SubElement(xmlroot, "permissions")
                xmlchild.text = self.ConvertUserFriendlyPermissions(st[ST_MODE])

                # User and Group
                username = pwd.getpwuid(st[ST_UID])[0]
                groupname = grp.getgrgid(st[ST_GID])[0]
                xmlchild = etree.SubElement(xmlroot, "owner")
                xmlchild.text = "%s:%s" % (username, groupname)

                ajaxlink = self.getURL(self._relpath, content_mode="ajax")
                xmlchild = etree.SubElement(xmlroot, "contentinfo", ajaxlink=ajaxlink, offset=str(0), numofoffsets="20", size=str(file_size))

                # Contents of File
                xmlchild = etree.SubElement(xmlroot, "contents")
                f = open(self._fullpath, 'rb')
                myfilter = ''.join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)])
                for line in range(0, file_size, 16)[:20]:
                    data = f.read(16)
                    newtr = etree.SubElement(xmlchild, "bin")
                    newtd = etree.SubElement(newtr, "offset")
                    newtd.text = "%08x" % line
                    newtd = etree.SubElement(newtr, "hex")
                    for x in data:
                        hexelem = etree.SubElement(newtd, "hexelem")
                        hexelem.text = "%02x" % ord(x)
                        pass
                    newtd = etree.SubElement(newtr, "str")
                    for x in data:
                        strelem = etree.SubElement(newtd, "strelem")
                        strelem.text = "%s" % ((ord(x) <= 127 and myfilter[ord(x)]) or '.')
                        pass
                    pass
                f.close()

                return xmlroot
        elif self._content_mode == "ajax":
            if "offset" not in self._web_support.req.form:
                offset = 0
                pass
            else:
                offset = int(self._web_support.req.form['offset'].value)
                pass
            if "lines" not in self._web_support.req.form:
                lines = 20
                pass
            else:
                lines = int(self._web_support.req.form['lines'].value)
                pass
            xmlroot = etree.Element('{%s}binary' % self._namespace_uri, name=os.path.basename(self._relpath), resurl=self._web_support.resurl)
            xmlchild = etree.SubElement(xmlroot, "contents")
            f = open(self._fullpath, 'rb')
            myfilter = ''.join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)])
            if offset is not 0:
                f.seek(offset)
                pass
            for line in range(offset, os.path.getsize(self._fullpath), 16)[:lines]:
                data = f.read(16)
                newtr = etree.SubElement(xmlchild, "bin")
                newtd = etree.SubElement(newtr, "offset")
                newtd.text = "%08x" % line
                newtd = etree.SubElement(newtr, "hex")
                for x in data:
                    hexelem = etree.SubElement(newtd, "hexelem")
                    hexelem.text = "%02x" % ord(x)
                    pass
                newtd = etree.SubElement(newtr, "str")
                for x in data:
                    strelem = etree.SubElement(newtd, "strelem")
                    strelem.text = "%s" % ((ord(x) <= 127 and myfilter[ord(x)]) or '.')
                    pass
                pass
            f.close()
            return xmlroot
        elif self._content_mode == "summary" or self._content_mode == "title":
            link = self.getURL(self._relpath)
            xmlroot = etree.Element('{http://thermal.cnde.iastate.edu/databrowse/default}default', xmlns="http://thermal.cnde.iastate.edu/databrowse/default", name=os.path.basename(self._relpath), href=link)
            return xmlroot
        elif self._content_mode == "raw":
            if "stream" in self._web_support.req.form:
                return self.streamGenerator()
            else:
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
