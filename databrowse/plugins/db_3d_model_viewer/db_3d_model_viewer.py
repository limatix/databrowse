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
""" plugins/handlers/db_3d_model_viewer.py - Generic 3D Model Viewer Handler """

import os
import os.path
import time
import magic
import platform
if platform.system() == "Linux":
    import pwd
    import grp
from stat import *
from lxml import etree
from databrowse.support.renderer_support import renderer_class


class db_3d_model_viewer(renderer_class):
    """ Generic 3D Model Files """

    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/modelfile"
    _namespace_local = "3dmodel"
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

                    xmlroot = etree.Element('{%s}modelfile' %
                                            self._namespace_uri,
                                            nsmap=self.nsmap,
                                            name=os.path.basename(self._relpath),
                                            resurl=self._web_support.resurl,
                                            downlink=downlink, icon=icon)

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
                    if platform.system() == "Linux":
                        username = pwd.getpwuid(st[ST_UID])[0]
                        groupname = grp.getgrgid(st[ST_GID])[0]
                        xmlchild = etree.SubElement(xmlroot, "owner", nsmap=self.nsmap)
                        xmlchild.text = "%s:%s" % (username, groupname)
                    import pdb
                    pdb.set_trace()
                    return xmlroot
            else:
                raise self.RendererException("Invalid Content Mode")
