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
## 19 Aug 2016; 88ABW-2016-4051.                                             ##
###############################################################################
""" plugins/renderers/db_checklist_chx.py - Generic Checklist Files """

import os
import os.path
from lxml import etree
from databrowse.support.renderer_support import renderer_class
import subprocess
import shutil
import sys
import imp


class db_checklist_editor(renderer_class):
    """ Generic Checklist Files """

    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/checklist"
    _namespace_local = "checklist"
    _default_content_mode = "full"
    _default_style_mode = "fill_out_checklist"
    _default_recursion_depth = 2

    def getContent(self):
        if self._caller != "databrowse":
            return None
        else:
            if "ajax" in self._web_support.req.form and "save" in self._web_support.req.form and self._style_mode == "fill_out_checklist":
                if "filename" in self._web_support.req.form and "destination" in self._web_support.req.form and "file" in self._web_support.req.form:
                    filename = self._web_support.req.form["filename"].value
                    destination = self._web_support.req.form["destination"].value
                    filestring = self._web_support.req.form["file"].value
                    if destination.startswith('/'):
                        fullpath = os.path.abspath(destination)
                    else:
                        fullpath = os.path.abspath(self._web_support.dataroot + "/" + destination)
                    fullfilename = os.path.abspath(fullpath + "/" + filename)
                    fullpath = os.path.dirname(fullfilename)
                    if filename == "":
                        self._web_support.req.output = "Error Saving File:  Filename Cannot Be Blank"
                        self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                        return [self._web_support.req.return_page()]                        
                    if os.path.exists(fullfilename) and os.path.isdir(fullfilename):
                        self._web_support.req.output = "Error Saving File:  Full Path '%s' is an Existing Directory" % fullfilename
                        self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                        return [self._web_support.req.return_page()]
                    if not fullpath.startswith(self._web_support.dataroot):
                        self._web_support.req.output = "Error Saving File:  Attempt to Save File Outside of Dataroot"
                        self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                        return [self._web_support.req.return_page()]
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
                    elif not os.path.isdir(fullpath):
                        self._web_support.req.output = "Error Saving File:  Requested Save Directory is an Existing File " + fullpath
                        self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                        return [self._web_support.req.return_page()]
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
                    (filedir,filename_nodir)=os.path.split(filename)
                    tempsavedir = os.tempnam(None, "dbchx")
                    fullfilename = os.path.join(tempsavedir, filename_nodir + ".chx")
                    os.mkdir(tempsavedir)
                    os.chdir(tempsavedir)
                    # This is temporary and BAD!  Fix this line below
                    filestring = filestring.replace('xmlns="http://thermal.cnde.iastate.edu/checklist"', 'xmlns="http://limatix.org/checklist"') 
                    chxparsed = etree.XML(filestring)
                    imagelist = chxparsed.xpath("//chx:checklist/chx:checkitem/chx:parameter[@name='image']", namespaces={"chx": "http://limatix.org/checklist"})
                    for image in imagelist:
                        image = image.text
                        image = image.translate(None, "\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f")
                        image = image.strip()
                        if image.startswith('/'):
                            imagepath = image
                        else:
                            imagepath = os.path.abspath(os.path.dirname(self._fullpath) + '/' + image)
                            shutil.copy(imagepath, tempsavedir)
                    f = open(fullfilename, "w")
                    f.write(filestring)
                    f.close()
                    try:
                        os.environ["HOME"] = "/home/www/.home"
                        chx2pdf = imp.load_source("chx2pdf", os.path.join(self._web_support.qautils, "bin/chx2pdf"))
                        chx2pdf.chx2pdf(fullfilename)
                    except Exception as err:
                        self._web_support.req.output = "Error Generating PDF:  " + str(err)
                        self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                        return [self._web_support.req.return_page()]
                    try:
                        f = open(os.path.join(tempsavedir, filename_nodir + ".pdf"), 'rb')
                        self._web_support.req.response_headers['Content-Type'] = 'application/pdf'
                        self._web_support.req.response_headers['Content-Length'] = str(self.getSize(os.path.join(tempsavedir, filename_nodir + ".pdf")))
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
            elif "ajax" in self._web_support.req.form and "save" in self._web_support.req.form and self._style_mode == "edit_checklist":
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
            elif self._content_mode == "full" and self._style_mode == "fill_out_checklist":
                #etree.register_namespace("chx", "http://thermal.cnde.iastate.edu/checklist")
                f = open(self._fullpath, 'r')
                xml = etree.parse(f)
                f.close()
                g = open(os.path.join(self._web_support.qautils, 'checklist/chx2html.xsl'), 'r')
                xsltransform = etree.parse(g)
                g.close()
                transform = etree.XSLT(xsltransform)
                if "dest" in self._web_support.req.form:
                    transformedxml = transform(xml, dest=etree.XSLT.strparam(self._web_support.req.form['dest'].value))
                else:
                    transformedxml = transform(xml)
                xmloutput = etree.XML(str(transformedxml))
                return xmloutput
            elif self._content_mode == "full" and self._style_mode =="edit_checklist":
                f = open(self._fullpath, 'r')
                xml = etree.parse(f)
                f.close()
                xmlroot = xml.getroot()
                templatefile = self.getURL("/SOPs/.src/checklist.xhtml", handler="db_default", content_mode="raw", ContentType="application/xml")
                xmlroot.set("templatefile", templatefile)
                return xmlroot
            else:
                raise self.RendererException("Invalid Content Mode")

    pass
