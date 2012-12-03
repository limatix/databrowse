#!/usr/bin/env python
###############################################################################
## Databrowse:  An Extensible Data Management Platform                       ##
## Copyright (C) 2012 Iowa State University                                  ##
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
""" plugins/renderers/dbr_default.py - Default Renderer - Basic Output for Any File """

import os
import os.path
import time
from stat import *
import amara.writers
import amara.writers.treewriter
import amara.writers.outputparameters
import xslt_support


class dbr_default:
    """ Default Renderer - Basic Output for Any File """

    _relpath = None
    _fullpath = None
    _web_support = None
    _handler_support = None

    _getContent_transform = r"""<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="resources/ag_web.xml"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:output method="xml" encoding="utf-8"/>
    <xsl:template match="/">
        <xsl:processing-instruction name="xml-stylesheet">type="text/xsl" href="resources/ag_web.xml"</xsl:processing-instruction>
        <body>
            <table>
                <tr><th colspan="2"><xsl:value-of select="file/filename"/></th></tr>
                <tr><td colspan="2"><xsl:value-of select="file/path"/></td></tr>
                <tr><td>Size: </td><td><xsl:value-of select="file/size"/> bytes</td></tr>
                <tr><td>Modified: </td><td><xsl:value-of select="file/mtime"/></td></tr>
                <tr><td>Accessed: </td><td><xsl:value-of select="file/atime"/></td></tr>
                <tr><td>Updated: </td><td><xsl:value-of select="file/ctime"/></td></tr>
            </table>
        </body>
    </xsl:template>
</xsl:stylesheet>
"""

    def __init__(self, relpath, fullpath, web_support, handler_support):
        """ Load all of the values provided by initialization """
        self._relpath = relpath
        self._fullpath = fullpath
        self._web_support = web_support
        self._handler_support = handler_support
        pass

    def getContent(self):
        """ Returns content when called by main application """

        try:
            st = os.stat(self._fullpath)
        except IOError:
            return "Failed To Get File Information: %s" % (self._fullpath)
        else:
            file_size = st[ST_SIZE]
            file_mtime = time.asctime(time.localtime(st[ST_MTIME]))
            file_ctime = time.asctime(time.localtime(st[ST_CTIME]))
            file_atime = time.asctime(time.localtime(st[ST_ATIME]))

            xmldoc = amara.writers.treewriter.treewriter(output_parameters=amara.writers.outputparameters.outputparameters(), base_uri=None)
            xmldoc.start_document()
            xmldoc.start_element(u'file')

            xmldoc.start_element(u'filename')
            xmldoc.text(os.path.basename(self._fullpath))
            xmldoc.end_element(u'filename')

            xmldoc.start_element(u'path')
            xmldoc.text(os.path.dirname(self._fullpath))
            xmldoc.end_element(u'path')

            xmldoc.start_element(u'size')
            xmldoc.text(str(file_size))
            xmldoc.end_element(u'size')

            xmldoc.start_element(u'mtime')
            xmldoc.text(file_mtime)
            xmldoc.end_element(u'mtime')

            xmldoc.start_element(u'ctime')
            xmldoc.text(file_ctime)
            xmldoc.end_element(u'ctime')

            xmldoc.start_element(u'atime')
            xmldoc.text(file_atime)
            xmldoc.end_element(u'atime')

            xmldoc.end_element(u'file')
            xmldoc.end_document()

            return xslt_support.ApplyXSLTTransform(self._web_support, self._getContent_transform, xmldoc.get_result())
        pass

    pass
