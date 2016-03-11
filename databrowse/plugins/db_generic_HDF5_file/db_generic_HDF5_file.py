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
""" plugins/renderers/db_xml_generic.py - Default Text Renderer """

import os
import os.path
import time
import pwd
import grp
from stat import *
from lxml import etree
import subprocess
from databrowse.support.renderer_support import renderer_class
import magic
import h5py
import base64
import matplotlib as mpl
mpl.use('Agg')
import pylab


class db_generic_HDF5_file(renderer_class):
    """ Default Renderer - Basic Output for Any XML File """

    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/hdf5"
    _namespace_local = "dbhdf"
    _default_content_mode = "full"
    _default_style_mode = "view_data"
    _default_recursion_depth = 2

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

                    xmlroot = etree.Element('{%s}dbhdf' % self._namespace_uri, nsmap=self.nsmap, name=os.path.basename(self._relpath), resurl=self._web_support.resurl, downlink=downlink, icon=icon)

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

                    # Contents of File
                    f = open(self._fullpath)
                    xmlchild = etree.SubElement(xmlroot, "contents", nsmap=self.nsmap)
                    output, error = subprocess.Popen(['/usr/bin/h5dump', '-x', '-H', self._fullpath], stdout=subprocess.PIPE).communicate()
                    xmlchild.append(etree.XML(output))
                    #xmlchild.text = f.read()

                    return xmlroot
            elif self._content_mode == "raw" and self._web_support.req.form['getimage'].value == "true" and 'hdfloc' in self._web_support.req.form:
                hdfpath = self._web_support.req.form['hdfloc'].value
                tagname = base64.urlsafe_b64encode(hdfpath)
                ext='png'
                if self.CacheFileExists(tagname, extension=ext):
                    size = os.path.getsize(self.getCacheFileName(tagname, extension=ext))
                    f = self.getCacheFileHandler('rb', tagname, extension=ext)
                    self._web_support.req.response_headers['Content-Type'] = 'image/png'
                    self._web_support.req.response_headers['Content-Length'] = str(size)
                    self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                    self._web_support.req.output_done = True
                    if 'wsgi.file_wrapper' in self._web_support.req.environ:
                        return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
                    else:
                        return iter(lambda: f.read(1024))
                else:
                    print(self._fullpath)
                    f = h5py.File(self._fullpath, 'r')
                    data = f.get(self._web_support.req.form['hdfloc'].value)
                    if len(data.value.shape) == 1:
                        pylab.plot(data.value)
                        imgf = self.getCacheFileHandler('w', tagname, 'png')
                        pylab.savefig(imgf)
                        imgf.close()
                        pylab.clf()
                    elif len(data.value.shape) == 2:
                        pylab.imshow(data.value, origin='lower')
                        imgf = self.getCacheFileHandler('w', tagname, 'png')
                        pylab.savefig(imgf)
                        imgf.close()
                        pylab.clf()
                    f.close()
                    size = os.path.getsize(self.getCacheFileName(tagname, extension=ext))
                    f = self.getCacheFileHandler('rb', tagname, extension=ext)
                    self._web_support.req.response_headers['Content-Type'] = 'image/png'
                    self._web_support.req.response_headers['Content-Length'] = str(size)
                    self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                    self._web_support.req.output_done = True
                    if 'wsgi.file_wrapper' in self._web_support.req.environ:
                        return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
                    else:
                        return iter(lambda: f.read(1024))
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
