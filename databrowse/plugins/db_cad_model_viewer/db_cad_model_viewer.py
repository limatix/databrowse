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
###############################################################################
""" plugins/handlers/db_serial_viewer.py - Generic 3D Model Viewer Handler """

import os
import os.path
import time
import magic
import subprocess
import platform
if platform.system() == "Linux":
    import pwd
    import grp
from stat import *
from lxml import etree
from databrowse.support.renderer_support import renderer_class


class db_cad_model_viewer(renderer_class):
    """ Generic 3D Model Files """

    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/dbmodel"
    _namespace_local = "dbmodel"
    _default_content_mode = "full"
    _default_style_mode = "view_model"
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
                    try:
                        magicstore = magic.open(magic.MAGIC_MIME)
                        magicstore.load()
                        contenttype = magicstore.file(
                            os.path.realpath(self._fullpath))  # real path to resolve symbolic links outside of dataroot
                    except AttributeError:
                        contenttype = magic.from_file(os.path.realpath(self._fullpath), mime=True)
                    if contenttype is None:
                        contenttype = "text/plain"
                    extension = os.path.splitext(self._fullpath)[1][1:]
                    icon = self._handler_support.GetIcon(contenttype, extension)
                    downlink = self.getURL(self._relpath, content_mode="raw", download="true")

                    try:
                        __import__('imp').find_module('NDI_app')
                        nditoolboxlink = self.getURL(self._relpath, content_mode="nditoolbox")
                    except ImportError:
                        nditoolboxlink = ""
                        pass

                    xmlroot = etree.Element('{%s}modelfile' %
                                            self._namespace_uri,
                                            nsmap=self.nsmap,
                                            name=os.path.basename(self._relpath),
                                            resurl=self._web_support.resurl,
                                            downlink=downlink,
                                            icon=icon,
                                            model=self.getURL(self._relpath, content_mode="raw", model="true"),
                                            extension=extension,
                                            nditoolboxlink=nditoolboxlink)

                    xmlchild = etree.SubElement(xmlroot, "filename", nsmap=self.nsmap)
                    xmlchild.text = os.path.basename(self._fullpath)

                    xmlchild = etree.SubElement(xmlroot, "path", nsmap=self.nsmap)
                    xmlchild.text = os.path.dirname(self._fullpath)

                    return xmlroot
            elif self._content_mode == "nditoolbox" and "ajax" in self._web_support.req.form:
                import NDI_app
                subprocess.Popen(['python', NDI_app.__file__, self._fullpath], cwd=os.path.dirname(NDI_app.__file__))

                self._web_support.req.output = "NDITOOlBOX Called Successfully"
                self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                return [self._web_support.req.return_page()]
            elif self._content_mode == "raw" and "download" in self._web_support.req.form:
                size = os.path.getsize(self._fullpath)
                try:
                    magicstore = magic.open(magic.MAGIC_MIME)
                    magicstore.load()
                    contenttype = magicstore.file(os.path.realpath(self._fullpath))  # real path to resolve symbolic links outside of dataroot
                except AttributeError:
                    contenttype = magic.from_file(os.path.realpath(self._fullpath), mime=True)
                if contenttype is None:
                    contenttype = "text/plain"
                f = open(self._fullpath, "rb")
                self._web_support.req.response_headers['Content-Type'] = contenttype
                self._web_support.req.response_headers['Content-Length'] = str(size)
                self._web_support.req.response_headers['Content-Disposition'] = "attachment; filename=" + os.path.basename(self._fullpath)
                self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                self._web_support.req.output_done = True
                if 'wsgi.file_wrapper' in self._web_support.req.environ:
                    return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
                else:
                    return iter(lambda: f.read(1024), '')
            elif self._content_mode == "raw" and "model" in self._web_support.req.form:
                f = open(self._fullpath, "rb")
                self._web_support.req.response_headers['Content-Disposition'] = "filename=" + os.path.basename(f.name)
                self._web_support.req.response_headers['Content-Length'] = str(os.fstat(f.fileno()).st_size)
                self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                self._web_support.req.output_done = True
                if 'wsgi.file_wrapper' in self._web_support.req.environ:
                    return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
                else:
                    return iter(lambda: f.read(1024), '')
            else:
                raise self.RendererException("Invalid Content Mode")
