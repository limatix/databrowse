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
""" plugins/renderers/db_image_generic.py - Default Image Renderer """

import os
import os.path
import time
import pwd
import grp
from stat import *
from lxml import etree
from databrowse.support.renderer_support import renderer_class
import magic
import Image
import StringIO
import databrowse.support.EXIF as EXIF
import databrowse.support.RMETA as RMETA


class db_image_viewer(renderer_class):
    """ Default Renderer - Basic Output for Any File """

    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/image"
    _namespace_local = "image"
    _default_content_mode = "full"
    _default_style_mode = "view_image"
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

                src = self.getURL(self._relpath, content_mode="raw", thumbnail="medium")
                href = self.getURL(self._relpath, content_mode="raw")
                downlink = self.getURL(self._relpath, content_mode="raw", download="true")

                xmlroot = etree.Element('{%s}image' % self._namespace_uri, nsmap=self.nsmap, name=os.path.basename(self._relpath), src=src, href=href, resurl=self._web_support.resurl, downlink=downlink)

                xmlchild = etree.SubElement(xmlroot, "filename", nsmap=self.nsmap)
                xmlchild.text = os.path.basename(self._fullpath)

                xmlchild = etree.SubElement(xmlroot, "path", nsmap=self.nsmap)
                xmlchild.text = os.path.dirname(self._fullpath)

                xmlchild = etree.SubElement(xmlroot, "filesize", nsmap=self.nsmap)
                xmlchild.text = self.ConvertUserFriendlySize(file_size)

                xmlchild = etree.SubElement(xmlroot, "mtime", nsmap=self.nsmap)
                xmlchild.text = file_mtime

                xmlchild = etree.SubElement(xmlroot, "ctime", nsmap=self.nsmap)
                xmlchild.text = file_ctime

                xmlchild = etree.SubElement(xmlroot, "atime", nsmap=self.nsmap)
                xmlchild.text = file_atime

                # File Permissions
                xmlchild = etree.SubElement(xmlroot, "permissions", nsmap=self.nsmap)
                xmlchild.text = self.ConvertUserFriendlyPermissions(st[ST_MODE])

                # User and Group
                username = pwd.getpwuid(st[ST_UID])[0]
                groupname = grp.getgrgid(st[ST_GID])[0]
                xmlchild = etree.SubElement(xmlroot, "owner", nsmap=self.nsmap)
                xmlchild.text = "%s:%s" % (username, groupname)

                magicstore = magic.open(magic.MAGIC_MIME)
                magicstore.load()
                contenttype = magicstore.file(self._fullpath)
                xmlchild = etree.SubElement(xmlroot, "contenttype", nsmap=self.nsmap)
                xmlchild.text = contenttype

                img = Image.open(self._fullpath)
                xmlchild = etree.SubElement(xmlroot, "imgsize", nsmap=self.nsmap)
                xmlchild.text = "%s x %s pixels" % img.size
                xmlchild = etree.SubElement(xmlroot, "imgmode", nsmap=self.nsmap)
                xmlchild.text = img.mode

                pmdfile = os.path.splitext(self._fullpath)[0]+'.pmd'
                if os.access(pmdfile, os.R_OK) and os.path.exists(pmdfile):
                    f = open(pmdfile, 'r')
                    pmddoc = etree.parse(f)
                    f.close()
                    pmdroot = pmddoc.getroot()
                    xmlroot.append(pmdroot)
                    pass

                f = open(self._fullpath, 'rb')
                exiftags = EXIF.process_file(f)
                f.seek(0)
                ricohtags = RMETA.process_file(f)
                f.close()

                xmlchild = etree.SubElement(xmlroot, "exiftags", nsmap=self.nsmap)
                x = exiftags.keys()
                x.sort()
                for tag in x:
                    if tag in ('JPEGThumbnail', 'TIFFThumbnail'):
                        continue
                    newxmltag = etree.SubElement(xmlchild, "tag", nsmap=self.nsmap, name=tag)
                    tagtext = exiftags[tag].printable
                    if not isinstance(tagtext, basestring):
                        newxmltag.text = repr(tagtext)
                    else:
                        newxmltag.text = tagtext
                    pass

                xmlchild = etree.SubElement(xmlroot, "ricohtags", nsmap=self.nsmap)
                for tag in ricohtags:
                    newxmltag = etree.SubElement(xmlchild, "tag", nsmap=self.nsmap, name=str(tag))
                    tagtext = ricohtags[tag]
                    if not isinstance(tagtext, basestring):
                        newxmltag.text = repr(tagtext)
                    else:
                        newxmltag.text = tagtext
                    pass

                return xmlroot
        elif self._content_mode == "summary" or self._content_mode == "title":
            link = self.getURL(self._relpath)
            src = self.getURL(self._relpath, content_mode="raw", thumbnail="gallery")
            href = self.getURL(self._relpath, content_mode="raw")
            downlink = self.getURL(self._relpath, content_mode="raw", download="true")
            xmlroot = etree.Element('{%s}image' % self._namespace_uri, nsmap=self.nsmap, name=os.path.basename(self._relpath), link=link, src=src, href=href, downlink=downlink)
            return xmlroot
        elif self._content_mode == "raw":
            magicstore = magic.open(magic.MAGIC_MIME)
            magicstore.load()
            contenttype = magicstore.file(self._fullpath)
            if "thumbnail" in self._web_support.req.form:
                ext = os.path.splitext(self._fullpath)[1]
                if ext == '.tif' or ext == '.tiff':
                    ext = '.png'
                    contenttype = 'image/png'
                if self._web_support.req.form['thumbnail'].value == "small":
                    tagname = "small"
                    newsize = (150, 150)
                elif self._web_support.req.form['thumbnail'].value == "medium":
                    tagname = "medium"
                    newsize = (300, 300)
                elif self._web_support.req.form['thumbnail'].value == "large":
                    tagname = "large"
                    newsize = (500, 500)
                elif self._web_support.req.form['thumbnail'].value == "gallery":
                    tagname = "gallery"
                    newsize = (201, 201)
                else:
                    tagname = "small"
                    newsize = (150, 150)
                if self.CacheFileExists(tagname, extension=ext):
                    size = os.path.getsize(self.getCacheFileName(tagname, extension=ext))
                    f = self.getCacheFileHandler('rb', tagname, extension=ext)
                    self._web_support.req.response_headers['Content-Type'] = contenttype
                    self._web_support.req.response_headers['Content-Length'] = str(size)
                    self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                    self._web_support.req.output_done = True
                    if 'wsgi.file_wrapper' in self._web_support.req.environ:
                        return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
                    else:
                        return iter(lambda: f.read(1024))
                else:
                    img = Image.open(self._fullpath)
                    format = img.format
                    img.thumbnail(newsize, Image.ANTIALIAS)
                    output = StringIO.StringIO()
                    img.save(output, format=format)
                    f = self.getCacheFileHandler('wb', tagname, extension=ext)
                    img.save(f)
                    f.close()
                    self._web_support.req.response_headers['Content-Type'] = contenttype
                    self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                    self._web_support.req.output_done = True
                    return [output.getvalue()]
            else:
                size = os.path.getsize(self._fullpath)
                f = open(self._fullpath, "rb")
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
