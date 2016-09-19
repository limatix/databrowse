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
""" plugins/renderers/db_wsgi_monthly_rpt.py - Hanlder for Monthly Reports """

import imp
import os
import os.path
import copy
from lxml import etree
from databrowse.support.renderer_support import renderer_class


class db_monthly_report_tool(renderer_class):
    """ Default Renderer for WSGI Scripts - Simply Passes Everything Off To The Script """

    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/monthrpt"
    _namespace_local = "monthrpt"
    _default_content_mode = "full"
    _default_style_mode = "complete_monthly_report"
    _default_recursion_depth = 2

    def dummy_start_response(self, status, headers, exc_info=None):
        self._web_support.req.status = status
        for item in headers:
            self._web_support.req.response_headers[item[0]] = item[1]
            pass
        self._web_support.req.response_headers['Content-Type'] = 'text/html'
        pass

    def getContent(self):
        if self._caller != "databrowse":
            return None
        else:
            if self._content_mode == "full":
                savedCWD = os.getcwd()
                tempCWD = os.path.dirname(self._fullpath)
                os.chdir(tempCWD)
                modulename = os.path.splitext(os.path.basename(self._fullpath))[0]
                module = imp.load_source(modulename, self._fullpath)
                environcopy = copy.copy(self._web_support.req.environ)
                environcopy['DATABROWSE_FILENAME'] = environcopy['SCRIPT_FILENAME']
                environcopy['SCRIPT_FILENAME'] = self._fullpath
                output = module.application(environcopy, self.dummy_start_response)
                os.chdir(savedCWD)
                del module
                del environcopy
                return etree.XML(output)
            elif self._content_mode == "raw":
                savedCWD = os.getcwd()
                tempCWD = os.path.dirname(self._fullpath)
                os.chdir(tempCWD)
                modulename = os.path.splitext(os.path.basename(self._fullpath))[0]
                module = imp.load_source(modulename, self._fullpath)
                environcopy = copy.copy(self._web_support.req.environ)
                environcopy['DATABROWSE_FILENAME'] = environcopy['SCRIPT_FILENAME']
                environcopy['SCRIPT_FILENAME'] = self._fullpath
                output = module.application(environcopy, self._web_support.req.start_response)
                os.chdir(savedCWD)
                self._web_support.req.output_done = True
                del module
                del environcopy
                return output
            else:
                raise self.RendererException("Invalid Content Mode")

    pass
