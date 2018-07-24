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
""" plugins/handlers/db_serial_viewer.py - Viewer for Arduino output logs """

import os
import os.path
import numpy as np
import time
import magic
import platform
if platform.system() == "Linux":
    import pwd
    import grp
from stat import *
from lxml import etree
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from databrowse.support.renderer_support import renderer_class


class db_serial_viewer(renderer_class):
    """ Generic Arduino Output Files """

    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/serial"
    _namespace_local = "serial"
    _default_content_mode = "full"
    _default_style_mode = "view_plots"
    _default_recursion_depth = 2

    def parse_log(self, fullpath):
        data = None
        headers = None
        timecalc = None
        with open(fullpath, "rb") as input_data:
            # Skips text before the beginning of the interesting block:
            for line in input_data:
                if line.strip().__contains__("START"):
                    headers = line.strip()[:-1].split("are ")[1].split(", ")
                    timecalc = line.strip().split(" ")
                    timecalc = timecalc[1][2:] + timecalc[2]

                    data = np.empty((0, len(headers)))
                    break
            # Reads text until the end of the block:
            for line in input_data:  # This keeps reading the file
                if line.strip().__contains__("END"):
                    break
                line_array = np.asarray(line.split(" "), dtype=np.float64)
                data = np.vstack((data, line_array))
        data_dict = {}
        for i in range(0, len(headers)):
            data_dict[headers[i]] = data[:, i]
        return timecalc, data_dict

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

                    xmlroot = etree.Element('{%s}logfile' %
                                            self._namespace_uri,
                                            nsmap=self.nsmap,
                                            name=os.path.basename(self._relpath),
                                            resurl=self._web_support.resurl,
                                            downlink=downlink,
                                            icon=icon)

                    xmlchild = etree.SubElement(xmlroot, "filename", nsmap=self.nsmap)
                    xmlchild.text = os.path.basename(self._fullpath)

                    xmlchild = etree.SubElement(xmlroot, "path", nsmap=self.nsmap)
                    xmlchild.text = os.path.dirname(self._fullpath)

                    # Datasets
                    dsetcontent = etree.SubElement(xmlroot, "dataset", nsmap=self.nsmap)
                    dsetcontent.set("url", self.getURL(self._relpath, content_mode="raw") + "&image")
                    return xmlroot
            elif self._content_mode == "raw" and "image" in self._web_support.req.form:
                timecalc, data = self.parse_log(self._fullpath)
                fprefix = os.path.splitext(os.path.basename(self._fullpath))[0]
                if not self.CacheFileExists(fprefix, 'png'):
                    plt.figure()
                    for header in data:
                        if header != "time":
                            x = data['time']
                            y = data[header]
                            plt.plot(x, y, label=header)
                    plt.xlabel('Time (s)')
                    plt.ylabel('Temperature (C)')
                    plt.title('Break Time: %s' % timecalc)
                    plt.legend(loc=4)
                    f = self.getCacheFileHandler('wb', fprefix, 'png')
                    plt.savefig(f)
                    pass

                f = self.getCacheFileHandler('rb', fprefix, 'png')

                contenttype = 'image/png'
                size = os.path.getsize(self.getCacheFileName(fprefix, 'png'))

                self._web_support.req.response_headers['Content-Disposition'] = "filename=" + os.path.basename(f.name)
                self._web_support.req.response_headers['Content-Type'] = contenttype
                self._web_support.req.response_headers['Content-Length'] = str(size)
                self._web_support.req.start_response(self._web_support.req.status,
                                                     self._web_support.req.response_headers.items())
                self._web_support.req.output_done = True
                if 'wsgi.file_wrapper' in self._web_support.req.environ:
                    return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
                else:
                    return iter(lambda: f.read(1024), '')
            else:
                raise self.RendererException("Invalid Content Mode")
