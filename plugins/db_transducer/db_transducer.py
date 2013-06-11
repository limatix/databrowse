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
import qrcode
import Image
import StringIO
import subprocess
from lxml import etree
from renderer_support import renderer_class


class db_transducer(renderer_class):
    """ Default Renderer - Basic Output for Any XML File """

    _namespace_uri = "http://thermal.cnde.iastate.edu/transducer"
    _namespace_local = "transducer"
    _default_content_mode = "full"
    _default_style_mode = "view_transducer_data"
    _default_recursion_depth = 2

    def getContent(self):
        if self._content_mode != "raw" and self._caller == "databrowse" and "ajax" not in self._web_support.req.form:
            f = open(self._fullpath, 'r')
            xml = etree.parse(f)
            f.close()
            filerelpath = os.path.join(os.path.dirname(self._relpath), os.path.splitext(os.path.basename(self._relpath))[0] + "_files")
            filefullpath = os.path.abspath(self._web_support.dataroot + '/' + filerelpath)
            xmlroot = xml.getroot()
            if os.path.exists(filefullpath) and self._style_mode == "view_transducer_data":
                import db_directory.db_directory as db_directory_module
                renderer = db_directory_module.db_directory(filerelpath, filefullpath, self._web_support, self._handler_support, "db_transducer", "db_directory", style_mode="empty")
                content = renderer.getContent()
                xmlroot.append(content)
            templatefile = self.getURL("/transducers/src/transducer.xhtml", handler="db_default", content_mode="raw", ContentType="application/xml")
            xmlroot.set("templatefile", templatefile)
            xmlroot.set("barcode", self.getURL(self._relpath, content_mode="raw", barcode="barcode"))
            xmlroot.set("printbarcode", self.getURL(self._relpath, content_mode="raw", printbarcode="printbarcode"))
            return xmlroot
        elif self._content_mode != "raw" and self._caller == "db_transducer_database" and self._style_mode == 'transducer_list':
            f = open(self._fullpath, 'r')
            xml = etree.parse(f)
            f.close()
            return xml.getroot()
        elif self._content_mode != "raw" and "ajax" in self._web_support.req.form and "save" in self._web_support.req.form:
            if "file" in self._web_support.req.form:
                filestring = self._web_support.req.form["file"].value
                fullfilename = self._fullpath
                # Let's check on the directory and make sure its writable and it exists
                if not os.access(os.path.dirname(fullfilename), os.W_OK):
                    self._web_support.req.output = "Error Saving File:  Save Directory Not Writable " + os.path.dirname(fullfilename)
                    self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                    return [self._web_support.req.return_page()]
                elif not os.access(fullfilename, os.W_OK):
                    self._web_support.req.output = "Error Saving File:  File Not Writable " + fullfilename
                    self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                    return [self._web_support.req.return_page()]
                else:
                    #Let's check on the file and make sure its writable and doesn't exist
                    if os.path.exists(fullfilename):
                        # rename old version into .1 .2. .3 etc.
                        filenum = 1
                        while os.path.exists("%s.bak.%.2d" % (fullfilename, filenum)):
                            filenum += 1
                            pass
                        os.rename(fullfilename, "%s.bak.%.2d" % (fullfilename, filenum))
                        pass

                    f = open(fullfilename, "w")
                    f.write(filestring)
                    f.close
                    self._web_support.req.output = "File Saved Successfully"
                    self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                    return [self._web_support.req.return_page()]
                pass
            else:
                self._web_support.req.output = "Error Saving File: Incomplete Request"
                self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                return [self._web_support.req.return_page()]
        elif self._content_mode == "raw":
            if "barcode" in self._web_support.req.form:
                if self.CacheFileExists("barcode", 'png'):
                    size = os.path.getsize(self.getCacheFileName("barcode", 'png'))
                    f = self.getCacheFileHandler('rb', "barcode", 'png')
                    self._web_support.req.response_headers['Content-Type'] = 'image/png'
                    self._web_support.req.response_headers['Content-Length'] = str(size)
                    self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                    self._web_support.req.output_done = True
                    if 'wsgi.file_wrapper' in self._web_support.req.environ:
                        return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
                    else:
                        return iter(lambda: f.read(1024))
                else:
                    tf = open(self._fullpath, "r")
                    tdbfile = etree.parse(tf)
                    tf.close()
                    tdbroot = tdbfile.getroot()
                    tdbelem = tdbroot.xpath('transducer:id', namespaces={"transducer": "http://thermal.cnde.iastate.edu/transducer"})[0]
                    img = qrcode.make('<xducer/>'+tdbelem.text)._img
                    img.thumbnail((201, 201), Image.ANTIALIAS)
                    output = StringIO.StringIO()
                    img.save(output, format="png")
                    f = self.getCacheFileHandler('wb', "barcode", 'png')
                    img.save(f, format="png")
                    f.close()
                    self._web_support.req.response_headers['Content-Type'] = 'image/png'
                    self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                    self._web_support.req.output_done = True
                    return [output.getvalue()]
            if "printbarcode" in self._web_support.req.form:
                try:
                    tf = open(self._fullpath, "r")
                    tdbfile = etree.parse(tf)
                    tf.close()
                    tdbroot = tdbfile.getroot()
                    tdbelem = tdbroot.xpath('transducer:id', namespaces={"transducer": "http://thermal.cnde.iastate.edu/transducer"})[0]
                    os.environ["HOME"] = "/home/www"
                    subprocess.call(["/usr/local/bin/printQRcode", '<xducer/>'+tdbelem.text])
                except Exception as err:
                    self._web_support.req.output = "Error Printing Barcode:  " + err
                    self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                    return [self._web_support.req.return_page()]
                else:
                    self._web_support.req.output = "Barcode Sent to Printer!"
                    self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                    return [self._web_support.req.return_page()]
            else:
                raise self.RendererException("Raw Mode is Not Supported by this Plugin")
        else:
            return None
        pass

    pass
