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
""" plugins/renderers/db_transducer_database.py - Basic Output for Any Folder """

import databrowse.plugins.db_directory.db_directory as db_directory_module
from lxml import etree
import os


class db_transducer_database(db_directory_module.db_directory):
    """ Image Directory Renderer """

    _default_content_mode = "title"
    _default_style_mode = "transducer_list"
    _default_recursion_depth = 1

    def __init__(self, relpath, fullpath, web_support, handler_support, caller, handlers, content_mode=_default_content_mode, style_mode=_default_style_mode, recursion_depth=_default_recursion_depth):
        if caller == "databrowse":
            self._namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/transducerdb"
            self._namespace_local = "transducerdb"
        else:
            self._namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/dir"
            self._namespace_local = "dir"
            self._disable_load_style = True
        if style_mode != "add_transducer":
            super(db_transducer_database, self).__init__(relpath, fullpath, web_support, handler_support, caller, handlers, content_mode, style_mode)
        else:
            super(db_directory_module.db_directory, self).__init__(relpath, fullpath, web_support, handler_support, caller, handlers, content_mode, style_mode)
        pass

    def getContent(self):
        if self._style_mode != "add_transducer":
            return super(db_transducer_database, self).getContent()
        else:
            if "ajax" in self._web_support.req.form and "save" in self._web_support.req.form:
                if "file" in self._web_support.req.form:
                    filestring = self._web_support.req.form["file"].value
                    xml = etree.XML(filestring)
                    transducertag = xml.xpath("/transducer:transducer/transducer:id/.", namespaces={"transducer": "http://thermal.cnde.iastate.edu/transducer"})
                    transducerid = transducertag[0].text
                    fullfilename = os.path.join(self._fullpath, transducerid + ".tdb")
                    # Let's check on the directory and make sure its writable and it exists
                    if not os.access(os.path.dirname(fullfilename), os.W_OK):
                        self._web_support.req.output = "Error Saving File:  Save Directory Not Writable " + os.path.dirname(fullfilename)
                        self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                        return [self._web_support.req.return_page()]
                    else:
                        #Let's check on the file and make sure its writable and doesn't exist
                        if os.path.exists(fullfilename):
                            self._web_support.req.output = "Error Saving File:  Transducer " + transducerid + " already exists"
                            self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                            return [self._web_support.req.return_page()]
                        else:
                            f = open(fullfilename, "w")
                            f.write(filestring)
                            f.close
                            os.makedirs(os.path.join(self._fullpath, transducerid + "_files"))
                            self._web_support.req.output = "File Saved Successfully"
                            self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                            return [self._web_support.req.return_page()]
                    pass
                else:
                    self._web_support.req.output = "Error Saving File: Incomplete Request"
                    self._web_support.req.response_headers['Content-Type'] = 'text/plain'
                    return [self._web_support.req.return_page()]
            else:
                xmlroot = etree.Element("{%s}transducerdb" % self._namespace_uri, nsmap=self.nsmap, templatefile=self.getURL("/transducers/src/transducer.xhtml", handler="db_default", content_mode="raw", ContentType="application/xml"))
                return xmlroot
        pass
    pass
