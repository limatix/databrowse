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
""" plugins/renderers/db_specimen_database.py - Basic Output for Any Folder """

import databrowse.plugins.db_directory.db_directory as db_directory_module
from lxml import etree
import os
from errno import EEXIST

try:
    import databrowse.plugins.db_mercurial_repository.db_mercurial_repository as hgmodule
    hgrepo = hgmodule.db_mercurial_repository
    hgavailable = True
except:
    hgavailable = False


class db_specimen_database(db_directory_module.db_directory):
    """ Image Directory Renderer """

    _default_content_mode = "title"
    _default_style_mode = "specimen_list"
    _default_recursion_depth = 1

    def __init__(self, relpath, fullpath, web_support, handler_support, caller, handlers, content_mode=_default_content_mode, style_mode=_default_style_mode, recursion_depth=_default_recursion_depth):
        if caller == "databrowse":
            self._namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/specimendb"
            self._namespace_local = "specimendb"
        else:
            self._namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/dir"
            self._namespace_local = "dir"
            self._disable_load_style = True
        if style_mode not in ["add_specimen", "add_specimen_group"]:
            tmpref = self.getDirectoryList
            self.getDirectoryList = self.getSpecimenDatabaseDirectoryList
            super(db_specimen_database, self).__init__(relpath, fullpath, web_support, handler_support, caller, handlers, content_mode, style_mode)
            self.getDirectoryList = tmpref
            if hgavailable:
                uncommitted = hgrepo.uncommittedlist(fullpath)
                if len(uncommitted) > 0:
                    self._xml.set('uncommitted', str(len(uncommitted)))
        else:
            super(db_directory_module.db_directory, self).__init__(relpath, fullpath, web_support, handler_support, caller, handlers, content_mode, style_mode)
        pass

    def getSpecimenDatabaseDirectoryList(self, fullpath, sort=None, order="asc"):
        """ Build a Sorted List of Files with Appropriate Files Removed """
        #print "getDirectoryList being called"
        reallist = os.listdir(fullpath)
        returnlist = [n for n in reallist if n.endswith('.sdb') or n.endswith('.sdg')]
        exec "returnlist.sort(%s%s)" % ("reverse=True" if order == "desc" else "reverse=False", ",key=%s" % sort if sort is not None else ",key=str.lower")
        return returnlist

    def getContent(self):
        if self._style_mode not in ["add_specimen", "add_specimen_group"]:
            return super(db_specimen_database, self).getContent()
        else:
            if "ajax" in self._web_support.req.form and "save" in self._web_support.req.form:
                if "file" in self._web_support.req.form and self._style_mode == 'add_specimen':
                    filestring = self._web_support.req.form["file"].value
                    xml = etree.XML(filestring)
                    specimentag = xml.xpath("/specimen:specimen/specimen:specimenid/.", namespaces={"specimen": "http://thermal.cnde.iastate.edu/specimen"})
                    dirtags = xml.xpath("/specimen:specimen/specimen:reldests/specimen:reldest", namespaces={"specimen":"http://thermal.cnde.iastate.edu/specimen"})
                    specimenid = specimentag[0].text
                    fullfilename = os.path.join(self._fullpath, specimenid + ".sdb")
                    # Let's check on the directory and make sure its writable and it exists
                    if not os.access(os.path.dirname(fullfilename), os.W_OK):
                        self._web_support.req.output = "Error Saving File:  Save Directory Not Writable " + os.path.dirname(fullfilename)
                        self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                        return [self._web_support.req.return_page()]
                    else:
                        #Let's check on the file and make sure its writable and doesn't exist
                        if os.path.exists(fullfilename):
                            self._web_support.req.output = "Error Saving File:  Specimen " + specimenid + " already exists"
                            self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                            return [self._web_support.req.return_page()]
                        else:
                            try:
                                for dirtag in dirtags:
                                    newdirname = None
                                    if dirtag.get('{http://www.w3.org/1999/xlink}href') is not None:
                                        newdirname = dirtag.get('{http://www.w3.org/1999/xlink}href')
                                    else:
                                        newdirname = dirtag.text 
                                    if newdirname is not None:
                                        os.makedirs(os.path.join(self._fullpath, newdirname))
                            except OSError as err:
                                if err.errno == EEXIST:  # Handle the Race Condition
                                    pass
                                else:
                                    self._web_support.req.output = "Error Creating Files Directory: " + str(err)
                                    self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                                    return [self._web_support.req.return_page()]
                            f = open(fullfilename, "w")
                            f.write(filestring)
                            f.close
                            self._web_support.req.output = "File Saved Successfully"
                            self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                            return [self._web_support.req.return_page()]
                    pass
                elif "file" in self._web_support.req.form and self._style_mode == 'add_specimen_group':
                    filestring = self._web_support.req.form["file"].value
                    xml = etree.XML(filestring)
                    specimentag = xml.xpath("/specimen:specimengroup/specimen:groupid/.", namespaces={"specimen": "http://thermal.cnde.iastate.edu/specimen"})
                    specimenid = specimentag[0].text
                    fullfilename = os.path.join(self._fullpath, specimenid + ".sdg")
                    # Let's check on the directory and make sure its writable and it exists
                    if not os.access(os.path.dirname(fullfilename), os.W_OK):
                        self._web_support.req.output = "Error Saving File:  Save Directory Not Writable " + os.path.dirname(fullfilename)
                        self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                        return [self._web_support.req.return_page()]
                    else:
                        #Let's check on the file and make sure its writable and doesn't exist
                        if os.path.exists(fullfilename):
                            self._web_support.req.output = "Error Saving File:  Specimen Group " + specimenid + " already exists"
                            self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                            return [self._web_support.req.return_page()]
                        else:
                            try:
                                os.makedirs(os.path.join(self._fullpath, specimenid + "_files"))
                            except OSError as err:
                                if err.errno == EEXIST:  # Handle the Race Condition
                                    pass
                                else:
                                    self._web_support.req.output = "Error Creating Files Directory: " + str(err)
                                    self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                                    return [self._web_support.req.return_page()]
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
            else:
                if self._style_mode == "add_specimen":
                    xmlroot = etree.Element("{%s}specimendb" % self._namespace_uri, nsmap=self.nsmap, templatefile=self.getURL("/specimens/src/specimen.xhtml", handler="db_default", content_mode="raw", ContentType="application/xml"))
                elif self._style_mode == "add_specimen_group":
                    xmlroot = etree.Element("{%s}specimendb" % self._namespace_uri, nsmap=self.nsmap, templatefile=self.getURL("/specimens/src/specimengroup.xhtml", handler="db_default", content_mode="raw", ContentType="application/xml"))
                return xmlroot
        pass
    pass
