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
""" plugins/renderers/db_dataguzzler.py - Default Renderer - Basic Output for Any Dataguzzler File """

import os
import os.path
from stat import *
from lxml import etree
from renderer_support import renderer_class
import magic
import dg_file as dgf
import struct

# These definitions should be synchronized with dg_dumpfile within dataguzzler
dgf_nestedchunks = set(["DATAGUZZ", "GUZZNWFM", "GUZZWFMD", "METADATA", "METDATUM", "SNAPSHOT", "SNAPSHTS", "VIBRDATA", "VIBFCETS", "VIBFACET"])
dgf_stringchunks = set(["WAVENAME", "METDNAME", "METDSTRV"])
dgf_int64chunks = set(["METDINTV", "WFMDIMNS"])
dgf_float64chunks = set(["METDDBLV"])


class db_dataguzzler(renderer_class):
    """ Default Renderer - Basic Output for Any Dataguzzler File """

    _namespace_uri = "http://thermal.cnde.iastate.edu/dataguzzler"
    _namespace_local = "dg"
    _default_content_mode = "detailed"
    _default_style_mode = "list"
    _default_recursion_depth = 2

    def dumpxmlchunk(self, dgfh, nestdepth=-1):
        ellist = []

        Chunk = dgf.nextchunk(dgfh)
        while Chunk:
            newel = etree.Element("{%s}%s" % (self._namespace_uri, Chunk.Name))
            if (Chunk.Name in dgf_nestedchunks):
                if nestdepth > 0:
                    nestedchunks = self.dumpxmlchunk(dgfh, nestdepth-1)
                    for nestedchunk in nestedchunks:
                        newel.append(nestedchunk)
                        pass
                    pass
                else:
                    nestedchunks = self.dumpxmlchunk(dgfh, -1)
                    for nestedchunk in nestedchunks:
                        newel.append(nestedchunk)
                        pass
                    pass
                pass
            elif Chunk.Name in dgf_stringchunks:
                newel.text = dgf.readdata(dgfh, Chunk.ChunkLen)
                pass
            elif Chunk.Name in dgf_int64chunks:
                textdata = ""
                for cnt in range(Chunk.ChunkLen/8):
                    textdata += "%d\n" % (struct.unpack("@Q", dgf.readdata(dgfh, 8)))
                    pass
                newel.text = textdata
                pass
            elif Chunk.Name in dgf_float64chunks:
                textdata = ""
                for cnt in range(Chunk.ChunkLen/8):
                    textdata += "%.10g\n" % (struct.unpack("@d", dgf.readdata(dgfh, 8)))
                    pass
                newel.text = textdata
                pass
            else:
                newel.text = " %d bytes\n" % (Chunk.ChunkLen)
                pass
            dgf.chunkdone(dgfh, None)
            Chunk = dgf.nextchunk(dgfh)
            ellist.append(newel)
            pass
        return ellist

    def getContent(self):
        if self._content_mode is "title":
            return None  # just use filename
        elif self._content_mode is "detailed" or self._content_mode is "summary":
            nestdepth = -1
            if self._content_mode is "summary":
                nestdepth = 3
                pass

            dgfh = dgf.open(self._fullpath)
            if dgfh:
                xmlchunk = self.dumpxmlchunk(dgfh, nestdepth=nestdepth)
                dgf.close(dgfh)
                pass
            assert(len(xmlchunk) == 1)

            extension = os.path.splitext(self._fullpath)[1][1:]
            icon = self._handler_support.GetIcon('application/octet-stream', extension)

            downlink = self.getURL(self._relpath, content_mode="raw", download="true")

            etree.register_namespace("dbdg", "http://thermal.cnde.iastate.edu/databrowse/dataguzzler")

            xmlroot = etree.Element('{%s}dbdg' % "http://thermal.cnde.iastate.edu/databrowse/dataguzzler", name=os.path.basename(self._relpath), resurl=self._web_support.resurl, downlink=downlink, icon=icon)
            xmlroot.append(xmlchunk[0])

            return xmlroot

        elif self._content_mode == "raw":
            size = os.path.getsize(self._fullpath)
            magicstore = magic.open(magic.MAGIC_NONE)
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
