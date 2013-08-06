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
""" plugins/renderers/db_xlg_viewer.py - Experiment Log Viewer """

import os
import os.path
from lxml import etree
from databrowse.support.renderer_support import renderer_class
import magic


class db_datacollect_v2_viewer(renderer_class):
    """ Experiment Log Viewer """

    _namespace_uri = "http://thermal.cnde.iastate.edu/datacollect"
    _namespace_local = "dc"
    _default_content_mode = "full"
    _default_style_mode = "log_view"
    _default_recursion_depth = 2

    def getContent(self):
        if self._caller != "databrowse":
            return None
        else:
            if self._content_mode == "full":
                # Contents of File
                f = open(self._fullpath)
                xmlroot = etree.XML(f.read())
                # Resolve URL to Files Directory
                reldest = xmlroot.xpath('dc:summary/dc:reldest', namespaces={'dc': 'http://thermal.cnde.iastate.edu/datacollect'})[0].text
                reldesturl = self.getURL(os.path.abspath(os.path.join(os.path.dirname(self._relpath), reldest)))
                xmlroot.set('reldesturl', reldesturl)
                # Resolve URLs for Config Files
                configlist = xmlroot.xpath('dc:configstr', namespaces={'dc': 'http://thermal.cnde.iastate.edu/datacollect'})
                for item in configlist:
                    try:
                        fname = item.get('fname')
                        fnames = item.get('fnames')
                        if fname:
                            path = os.path.realpath(fname)
                            if path.startswith(self._web_support.dataroot) and os.access(path, os.R_OK) and os.path.exists(path):
                                relpath = path.replace(self._web_support.dataroot, '')
                                url = self.getURL(relpath)
                                item.set('url', url)
                        elif fnames:
                            if fnames[0] == '[' and fnames[-1] == "]":
                                urls = []
                                fnamelist = fnames[1:-1].split(',')
                                for fname in fnamelist:
                                    fname = fname.replace("'", "").replace('"', "").strip()
                                    path = os.path.realpath(fname)
                                    if path.startswith(self._web_support.dataroot) and os.access(path, os.R_OK) and os.path.exists(path):
                                        relpath = path.replace(self._web_support.dataroot, '')
                                        url = self.getURL(relpath)
                                        urls.append(url)
                                    else:
                                        urls.append("")
                                item.set('urls', repr(urls))
                    except:
                        pass
                # Resolve URLs for Specimen Database
                specimenlist = xmlroot.xpath('//dc:specimen', namespaces={"dc": 'http://thermal.cnde.iastate.edu/datacollect', "dcv": 'http://thermal.cnde.iastate.edu/dcvalue'})
                for item in specimenlist:
                    if item.text:
                        relpath = '/specimens/' + item.text + '.sdb'
                        if os.access(os.path.abspath(self._web_support.dataroot + "/" + relpath), os.R_OK) and os.path.exists(os.path.abspath(self._web_support.dataroot + "/" + relpath)):
                            url = self.getURL(relpath)
                            item.set('url', url)
                # Resolve URLs for Transducer Database
                transducerlist = xmlroot.xpath('//dc:xducer', namespaces={"dc": 'http://thermal.cnde.iastate.edu/datacollect', "dcv": 'http://thermal.cnde.iastate.edu/dcvalue'})
                for item in transducerlist:
                    if item.text:
                        relpath = '/transducers/' + item.text + '.tdb'
                        if os.access(os.path.abspath(self._web_support.dataroot + "/" + relpath), os.R_OK) and os.path.exists(os.path.abspath(self._web_support.dataroot + "/" + relpath)):
                            url = self.getURL(relpath)
                            item.set('url', url)
                f.close()
                return xmlroot
            elif self._content_mode == "raw":
                size = os.path.getsize(self._fullpath)
                magicstore = magic.open(magic.MAGIC_MIME)
                magicstore.load()
                contenttype = magicstore.file(self._fullpath)
                f = open(self._fullpath, "rb")
                self._web_support.req.response_headers['Content-Type'] = contenttype
                self._web_support.req.response_headers['Content-Length'] = str(size)
                self._web_support.req.response_headers['Content-Disposition'] = "attachment; filename=" + os.path.basename(self._fullpath)
                self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                self._web_support.req.output_done = True
                if 'wsgi.file_wrapper' in self._web_support.req.environ:
                    return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
                else:
                    return iter(lambda: f.read(1024))
            else:
                raise self.RendererException("Invalid Content Mode")
            pass

    pass
