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
""" plugins/renderers/dbr_checklist_chx.py - Generic Checklist Files """

import os
import os.path
from lxml import etree
from renderer_support import renderer_class
import subprocess
import shutil
import sys
import imp


class dbr_checklist_chx(renderer_class):
    """ Generic Checklist Files """

    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/checklist"
    _namespace_local = "checklist"
    _default_content_mode = "full"
    _default_style_mode = "full"
    _default_recursion_depth = 2

    def getContent(self):
        if "ajax" in self._web_support.req.form and "save" in self._web_support.req.form:
            if "filename" in self._web_support.req.form and "destination" in self._web_support.req.form and "file" in self._web_support.req.form:
                filename = self._web_support.req.form["filename"].value
                destination = self._web_support.req.form["destination"].value
                filestring = self._web_support.req.form["file"].value
                if destination.startswith('/'):
                    fullpath = os.path.abspath(destination)
                else:
                    fullpath = os.path.abspath(self._web_support.dataroot + "/" + destination)
                fullfilename = os.path.abspath(fullpath + "/" + filename)
                if not fullpath.startswith(self._web_support.dataroot):
                    raise self.RendererException("Attempt to Save File Outside of Dataroot")
                # Let's check on the directory and make sure its writable and it exists
                if not os.access(fullpath, os.W_OK) and os.path.exists(fullpath):
                    self._web_support.req.output = "Error Saving File:  Save Directory Not Writable " + fullpath
                    self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                    return [self._web_support.req.return_page()]
                elif not os.path.exists(fullpath):
                    try:
                        os.makedirs(fullpath)
                    except:
                        self._web_support.req.output = "Error Saving File:  Unable to Create Directory " + fullpath
                        self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                        return [self._web_support.req.return_page()]
                    pass
                else:
                    #Let's check on the file and make sure its writable and doesn't exist
                    if os.path.exists(fullfilename):
                        # rename old version into .1 .2. .3 etc.
                        filenum = 1
                        while os.path.exists("%s.%.2d" % (fullfilename, filenum)):
                            filenum += 1
                            pass
                        os.rename(fullfilename, "%s.%.2d" % (fullfilename, filenum))
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
        elif "ajax" in self._web_support.req.form and "pdf" in self._web_support.req.form:
            if all(k in self._web_support.req.form for k in ("file", "specimen", "perfby", "date", "dest")):
                filestring = self._web_support.req.form["file"].value
                if 'filename' in self._web_support.req.form:
                    upfilename = self._web_support.req.form["filename"].value
                else:
                    upfilename = "chxfromweb.chx"
                filename = os.path.splitext(upfilename)[0]
                tempsavedir = os.tempnam(None, "dbchx")
                fullfilename = os.path.join(tempsavedir, filename + ".chx")
                os.mkdir(tempsavedir)
                os.chdir(tempsavedir)
                chxparsed = etree.XML(filestring)
                imagelist = chxparsed.xpath("//chx:checklist/chx:checkitem/chx:parameter[@name='image']", namespaces={"chx": "http://thermal.cnde.iastate.edu/checklist"})
                for image in imagelist:
                    image = image.text
                    image = image.translate(None, "\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f")
                    image = image.strip()
                    imagepath = os.path.abspath(os.path.dirname(self._fullpath) + '/' + image)
                    shutil.copy(imagepath, tempsavedir)
                f = open(fullfilename, "w")
                f.write(filestring)
                f.close()
                try:
                    chx2pdf = imp.load_source("chx2pdf", "/usr/local/QAutils/bin/chx2pdf")
                    chx2pdf.chx2pdf(fullfilename)
                except Exception as err:
                    self._web_support.req.output = "Error Generating PDF:  " + str(err)
                    self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                    return [self._web_support.req.return_page()]
                try:
                    f = open(os.path.join(tempsavedir, filename + ".pdf"), 'rb')
                    self._web_support.req.response_headers['Content-Type'] = 'application/pdf'
                    self._web_support.req.response_headers['Content-Length'] = str(self.getSize(os.path.join(tempsavedir, filename + ".pdf")))
                    self._web_support.req.response_headers['Content-Disposition'] = "attachment; filename=" + filename + ".pdf"
                    self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                    self._web_support.req.output_done = True
                    if 'wsgi.file_wrapper' in self._web_support.req.environ:
                        return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
                    else:
                        return iter(lambda: f.read(1024))
                except Exception as err:
                    self._web_support.req.output = "Error Generating PDF:  " + err
                    self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                    return [self._web_support.req.return_page()]
            else:
                self._web_support.req.output = "Error Generating PDF: Incomplete Request"
                self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                return [self._web_support.req.return_page()]
        elif self._content_mode is "summary" or self._content_mode is "detailed" or self._content_mode is "title":
            link = self.getURL(self._relpath)
            xmlroot = etree.Element('{%s}checklist' % self._namespace_uri, name=os.path.basename(self._relpath), href=link)
            return xmlroot
        elif self._content_mode is "full":
            etree.register_namespace("chx", "http://thermal.cnde.iastate.edu/checklist")
            f = open(self._fullpath, 'r')
            xml = etree.parse(f)
            f.close()
            g = open('/usr/local/QAutils/checklist/chx2html.xsl', 'r')
            xsltransform = etree.parse(g)
            g.close()
            transformedxml = xml.xslt(xsltransform)
            xmloutput = etree.XML(str(transformedxml))
            return xmloutput
        else:
            raise self.RendererException("Invalid Content Mode")

    pass
