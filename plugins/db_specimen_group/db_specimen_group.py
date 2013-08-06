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


class db_specimen_group(renderer_class):
    """ Default Renderer - Basic Output for Any XML File """

    _namespace_uri = "http://thermal.cnde.iastate.edu/specimen"
    _namespace_local = "specimen"
    _default_content_mode = "full"
    _default_style_mode = "view_specimen_group"
    _default_recursion_depth = 2

    def getContent(self):
        if self._content_mode != "raw" and self._caller == "databrowse" and "ajax" not in self._web_support.req.form:
            f = open(self._fullpath, 'r')
            xml = etree.parse(f)
            f.close()
            filerelpath = os.path.join(os.path.dirname(self._relpath), os.path.splitext(os.path.basename(self._relpath))[0] + "_files")
            filefullpath = os.path.abspath(self._web_support.dataroot + '/' + filerelpath)
            xmlroot = xml.getroot()
            if os.path.exists(filefullpath) and self._style_mode == "view_specimen_data":
                import db_directory.db_directory as db_directory_module
                renderer = db_directory_module.db_directory(filerelpath, filefullpath, self._web_support, self._handler_support, "db_specimen_group", "db_directory", style_mode="empty")
                content = renderer.getContent()
                xmlroot.append(content)
            templatefile = self.getURL("/specimens/src/specimengroup.xhtml", handler="db_default", content_mode="raw", ContentType="application/xml")
            xmlroot.set("templatefile", templatefile)
            xmlroot.set("barcode", self.getURL(self._relpath, content_mode="raw", barcode="barcode"))
            xmlroot.set("printbarcode", self.getURL(self._relpath, content_mode="raw", printbarcode="printbarcode"))
            return xmlroot
        elif self._content_mode != "raw" and self._caller == "db_specimen_database" and self._style_mode == 'specimen_group_list':
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
        elif self._content_mode != "raw" and "ajax" in self._web_support.req.form and "addactionitem" in self._web_support.req.form:
            if not "date" in self._web_support.req.form or self._web_support.req.form['date'].value == "":
                self._web_support.req.output = "Date is a Required Field"
                self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                return [self._web_support.req.return_page()]
            elif not "perfby" in self._web_support.req.form or self._web_support.req.form['perfby'].value == "":
                self._web_support.req.output = "Performed By is a Required Field"
                self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                return [self._web_support.req.return_page()]
            elif not "action" in self._web_support.req.form or self._web_support.req.form['action'].value == "":
                self._web_support.req.output = "Action is a Required Field"
                self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                return [self._web_support.req.return_page()]
            else:
                fullfilename = self._fullpath
                xmltree = etree.parse(fullfilename)
                xmlroot = xmltree.getroot()
                actionlog = xmlroot.xpath("specimen:actionlog", namespaces={"specimen": "http://thermal.cnde.iastate.edu/specimen"})
                if actionlog:
                    actionlog = actionlog[0]
                else:
                    actionlog = etree.SubElement(xmlroot, "actionlog")
                actionevent = etree.SubElement(actionlog, "actionevent")
                actiondate = etree.SubElement(actionevent, "date")
                actiondate.text = self._web_support.req.form["date"].value
                actionperfby = etree.SubElement(actionevent, "perfby")
                actionperfby.text = self._web_support.req.form["perfby"].value
                actionaction = etree.SubElement(actionevent, "action")
                actionaction.text = self._web_support.req.form["action"].value
                actionnotes = etree.SubElement(actionevent, "notes")
                actionnotes.text = self._web_support.req.form["notes"].value

                # Let's check on the directory and make sure its writable and it exists
                if not os.access(os.path.dirname(fullfilename), os.W_OK):
                    self._web_support.req.output = "Save Directory Not Writable " + os.path.dirname(fullfilename)
                    self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                    return [self._web_support.req.return_page()]
                elif not os.access(fullfilename, os.W_OK):
                    self._web_support.req.output = "File Not Writable " + fullfilename
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
                f.write(etree.tostring(xmltree))
                f.close

                self._web_support.req.output = "Action Item Added Successfully"
                self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                return [self._web_support.req.return_page()]
        elif self._content_mode == "raw":
            raise self.RendererException("Raw Mode is Not Supported by this Plugin")
        else:
            return None
        pass

    pass
