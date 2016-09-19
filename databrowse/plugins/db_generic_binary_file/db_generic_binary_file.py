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
""" plugins/renderers/db_binary_generic.py - Default Binary Renderer """

import os
import os.path
import time
import pwd
import grp
from stat import *
from lxml import etree
from databrowse.support.renderer_support import renderer_class
import magic


class db_generic_binary_file(renderer_class):
    """ Default Renderer - Basic Output for Any Binary File """

    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/binary"
    _namespace_local = "binary"
    _default_content_mode = "full"
    _default_style_mode = "binary_preview"
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
        if self._caller != "databrowse":
            return None
        else:
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
                    magicstore = magic.open(magic.MAGIC_MIME)
                    magicstore.load()
                    contenttype = magicstore.file(self._fullpath)
                    extension = os.path.splitext(self._fullpath)[1][1:]
                    icon = self._handler_support.GetIcon(contenttype, extension)

                    downlink = self.getURL(self._relpath, content_mode="raw", download="true")

                    xmlroot = etree.Element('{%s}binary' % self._namespace_uri, nsmap=self.nsmap, name=os.path.basename(self._relpath), resurl=self._web_support.resurl, downlink=downlink, icon=icon)

                    xmlchild = etree.SubElement(xmlroot, "filename", nsmap=self.nsmap)
                    xmlchild.text = os.path.basename(self._fullpath)

                    xmlchild = etree.SubElement(xmlroot, "path", nsmap=self.nsmap)
                    xmlchild.text = os.path.dirname(self._fullpath)

                    xmlchild = etree.SubElement(xmlroot, "size", nsmap=self.nsmap)
                    xmlchild.text = self.ConvertUserFriendlySize(file_size)

                    xmlchild = etree.SubElement(xmlroot, "mtime", nsmap=self.nsmap)
                    xmlchild.text = file_mtime

                    xmlchild = etree.SubElement(xmlroot, "ctime", nsmap=self.nsmap)
                    xmlchild.text = file_ctime

                    xmlchild = etree.SubElement(xmlroot, "atime", nsmap=self.nsmap)
                    xmlchild.text = file_atime

                    # Content Type
                    xmlchild = etree.SubElement(xmlroot, "contenttype", nsmap=self.nsmap)
                    xmlchild.text = contenttype

                    # File Permissions
                    xmlchild = etree.SubElement(xmlroot, "permissions", nsmap=self.nsmap)
                    xmlchild.text = self.ConvertUserFriendlyPermissions(st[ST_MODE])

                    # User and Group
                    username = pwd.getpwuid(st[ST_UID])[0]
                    groupname = grp.getgrgid(st[ST_GID])[0]
                    xmlchild = etree.SubElement(xmlroot, "owner", nsmap=self.nsmap)
                    xmlchild.text = "%s:%s" % (username, groupname)

                    ajaxlink = self.getURL(self._relpath, content_mode="ajax")
                    xmlchild = etree.SubElement(xmlroot, "contentinfo", nsmap=self.nsmap, ajaxlink=ajaxlink, offset=str(0), numofoffsets="20", size=str(file_size))

                    # Contents of File
                    xmlchild = etree.SubElement(xmlroot, "contents", nsmap=self.nsmap)
                    f = open(self._fullpath, 'rb')
                    myfilter = ''.join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)])
                    for line in range(0, file_size, 16)[:20]:
                        data = f.read(16)
                        newtr = etree.SubElement(xmlchild, "bin", nsmap=self.nsmap)
                        newtd = etree.SubElement(newtr, "offset", nsmap=self.nsmap)
                        newtd.text = "%08x" % line
                        newtd = etree.SubElement(newtr, "hex", nsmap=self.nsmap)
                        for x in data:
                            hexelem = etree.SubElement(newtd, "hexelem", nsmap=self.nsmap)
                            hexelem.text = "%02x" % ord(x)
                            pass
                        newtd = etree.SubElement(newtr, "str", nsmap=self.nsmap)
                        for x in data:
                            strelem = etree.SubElement(newtd, "strelem", nsmap=self.nsmap)
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
                xmlroot = etree.Element('{%s}binary' % self._namespace_uri, nsmap=self.nsmap, name=os.path.basename(self._relpath), resurl=self._web_support.resurl)
                xmlchild = etree.SubElement(xmlroot, "contents", nsmap=self.nsmap)
                f = open(self._fullpath, 'rb')
                myfilter = ''.join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)])
                if offset is not 0:
                    f.seek(offset)
                    pass
                for line in range(offset, os.path.getsize(self._fullpath), 16)[:lines]:
                    data = f.read(16)
                    newtr = etree.SubElement(xmlchild, "bin", nsmap=self.nsmap)
                    newtd = etree.SubElement(newtr, "offset", nsmap=self.nsmap)
                    newtd.text = "%08x" % line
                    newtd = etree.SubElement(newtr, "hex", nsmap=self.nsmap)
                    for x in data:
                        hexelem = etree.SubElement(newtd, "hexelem", nsmap=self.nsmap)
                        hexelem.text = "%02x" % ord(x)
                        pass
                    newtd = etree.SubElement(newtr, "str", nsmap=self.nsmap)
                    for x in data:
                        strelem = etree.SubElement(newtd, "strelem", nsmap=self.nsmap)
                        strelem.text = "%s" % ((ord(x) <= 127 and myfilter[ord(x)]) or '.')
                        pass
                    pass
                f.close()
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
