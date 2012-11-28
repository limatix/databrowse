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
""" plugins/renderers/dbr_directory_generic.py - Basic Output for Any Folder """

import os
import os.path
import amara.writers
import amara.writers.treewriter
import amara.writers.outputparameters
import xslt_support


class dbr_directory_generic:
    """ Default Folder Renderer - Basic Output for Any Folder """

    _relpath = None
    _fullpath = None
    _web_support = None
    _handler_support = None

    _getContent_transform = r"""<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="css/ag_web.xml"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:output method="xml" encoding="utf-8"/>
    <xsl:template match="/">
        <xsl:processing-instruction name="xml-stylesheet">type="text/xsl" href="css/ag_web.xml"</xsl:processing-instruction>
        <body>
            <b><xsl:value-of select="folder/@path"/></b><br/>
            <xsl:apply-templates select="folder/item"/>
        </body>
    </xsl:template>
    <xsl:template match="item">
        <a>
            <xsl:attribute name="href"><xsl:value-of select="./@href"/></xsl:attribute>
            <xsl:value-of select="."/>
        </a><br/>
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

        dirlist = os.listdir(self._fullpath)
        xmldoc = amara.writers.treewriter.treewriter(output_parameters=amara.writers.outputparameters.outputparameters(), base_uri=None)
        xmldoc.start_document()
        xmldoc.start_element(u'folder')
        xmldoc.attribute('path', self._fullpath)
        for item in dirlist:
            xmldoc.start_element(u'item')
            xmldoc.attribute('href', '?path=' + (self._relpath if self._relpath is not '/' else '') + '/' + item)
            xmldoc.text(item)
            xmldoc.end_element(u'item')
            pass
        xmldoc.end_element(u'folder')
        xmldoc.end_document()
        return xslt_support.ApplyXSLTTransform(self._web_support, self._getContent_transform, xmldoc.get_result())

    pass
