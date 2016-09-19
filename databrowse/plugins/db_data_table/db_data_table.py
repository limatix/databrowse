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
""" plugins/renderers/db_data_table - Plugin for Data Table Display """

import sys
import os
import glob
import zipfile
import tempfile
from lxml import etree
from databrowse.support.renderer_support import renderer_class

class db_data_table(renderer_class):
    """ Data Table Plugin Renderer """

    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/datatable"
    _namespace_local = "dt"
    _default_content_mode = "full"
    _default_style_mode = "view_table"
    _default_recursion_depth = 2
    _table_transform = r"""<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns="http://thermal.cnde.iastate.edu/databrowse/datatable" xmlns:dt="http://thermal.cnde.iastate.edu/databrowse/datatable" %s xmlns:my="http://thermal.cnde.iastate.edu/databrowse/datatable/functions" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:dyn="http://exslt.org/dynamic" extension-element-prefixes="dyn my" version="1.0" exclude-result-prefixes="my">
    <xsl:output method='xml' indent='yes' omit-xml-declaration="no" version="1.0" media-type="application/xml" encoding="UTF-8"/>
    <xsl:variable name="siteurl" select="string('%s')" />
    <xsl:template match="table">
        <dt:datatable sourcefile="%s">
            <xsl:variable name="files" select="@filenamematch" />
            <xsl:variable name="rowmatch" select="rowmatch/@select" />
            <xsl:variable name="data" select="my:data($files)" />
            <xsl:variable name="assert" select="assert" />
            <xsl:variable name="cols" select="colspec"/>
            <xsl:attribute name="title">
                <xsl:choose>
                    <xsl:when test="@title"><xsl:value-of select="@title" /></xsl:when>
                    <xsl:otherwise>%s</xsl:otherwise>
                </xsl:choose>
            </xsl:attribute>
            <xsl:if test="description">
                <dt:description><xsl:copy-of select="description/node()"/></dt:description>
            </xsl:if>
            <dt:header>
                <xsl:for-each select="$cols">
                    <dt:coldef>
                        <xsl:if test="@tooltip">
                            <xsl:attribute name="tooltip"><xsl:value-of select="@tooltip" /></xsl:attribute>
                        </xsl:if>
                        <xsl:choose>
                            <xsl:when test="@label">
                                <xsl:value-of select="@label"/>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of select="@select"/>
                            </xsl:otherwise>
                        </xsl:choose>
                    </dt:coldef>
                </xsl:for-each>
            </dt:header>
            <xsl:apply-templates select="$data" mode="data">
                <xsl:with-param name="cols" select="$cols" />
                <xsl:with-param name="rowmatch" select="$rowmatch" />
                <xsl:with-param name="assert" select="$assert" />
            </xsl:apply-templates>
        </dt:datatable>
    </xsl:template>
    <xsl:template match="*" mode="data">
        <xsl:param name="cols" />
        <xsl:param name="rowmatch" />
        <xsl:param name="assert" />
        <xsl:for-each select="dyn:evaluate($rowmatch)">
            <xsl:variable name="data" select="." />
            <xsl:for-each select="$assert">
                <xsl:apply-templates mode="assert" select="$data">
                    <xsl:with-param name="assert" select="$assert/@select"/>
                </xsl:apply-templates>
            </xsl:for-each>
            <dt:row>
                <xsl:for-each select="$cols">
                    <dt:data><xsl:if test="@type"><xsl:attribute name="type"><xsl:value-of select="@type"/></xsl:attribute></xsl:if><xsl:if test="@url"><xsl:attribute name="url"><xsl:apply-templates mode="value" select="$data"><xsl:with-param name="select" select="@url"/></xsl:apply-templates></xsl:attribute></xsl:if><xsl:apply-templates mode="value" select="$data"><xsl:with-param name="select" select="@select"/></xsl:apply-templates></dt:data>
                </xsl:for-each>
            </dt:row>
        </xsl:for-each>
    </xsl:template>
    <xsl:template match="*" mode="value">
        <xsl:param name="select"/>
        <xsl:value-of select="dyn:evaluate($select)"/>
    </xsl:template>
    <xsl:template match="*" mode="url">
        <xsl:param name="select"/>
        <xsl:value-of select="dyn:evaluate($select)"/>
    </xsl:template>
    <xsl:template match="*" mode="assert">
        <xsl:param name="assert"/>
        <xsl:if test="not(dyn:evaluate($assert))">
            <xsl:if test="my:xmlassert($assert)"/>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
"""
    _ods_transform = r"""<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:dt="http://thermal.cnde.iastate.edu/databrowse/datatable" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0" xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0" xmlns:math="http://www.w3.org/1998/Math/MathML" xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0" xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0" xmlns:dom="http://www.w3.org/2001/xml-events" xmlns:xforms="http://www.w3.org/2002/xforms" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.0">
    <xsl:output method='xml' indent='yes'/>  
    <xsl:template match='dt:datatable'>
        <!-- Opendocument boilerplate -->
        <office:document-content office:version="1.0">  <!-- for ODF 1.2 conformance, change "1.0" to "1.2" -->
            <office:scripts/>
            <office:automatic-styles>
                <style:style style:name="co1" style:family="table-column">
                    <style:table-column-properties fo:break-before="auto" style:column-width="0.8925in"/>
                </style:style>
                <style:style style:name="ro1" style:family="table-row">
                    <style:table-row-properties style:row-height="0.1681in" fo:break-before="auto" style:use-optimal-row-height="true"/>
                </style:style>
                <style:style style:name="ta1" style:family="table" style:master-page-name="Default">
                    <style:table-properties table:display="true" style:writing-mode="lr-tb"/>
                </style:style>
            </office:automatic-styles>
            <office:body>
                <office:spreadsheet>
                    <table:table>
                        <xsl:attribute name="table:name">
                            <xsl:value-of select="@title"/>
                        </xsl:attribute>
                        <xsl:attribute name="table:style-name">ta1</xsl:attribute>
                        <xsl:attribute name="table:print">false</xsl:attribute>
                        <table:table-column table:style-name="co1" table:default-cell-style-name="Default"/>
                        <table:table-row table:style-name="ro1">
                            <xsl:for-each select="dt:header/dt:coldef">
                                <table:table-cell office:value-type="string">
                                    <text:p><xsl:value-of select="." /></text:p>
                                </table:table-cell>
                            </xsl:for-each>
                        </table:table-row>
                        <xsl:for-each select="dt:row">
                            <table:table-row table:style-name="ro1">
                                <xsl:for-each select="dt:data">
                                    <table:table-cell>
                                        <xsl:choose>
                                            <xsl:when test="@type='numeric'">
                                                <xsl:attribute name="office:value-type">float</xsl:attribute>
                                                <xsl:attribute name="office:value"><xsl:value-of select="normalize-space(.)"/></xsl:attribute>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:attribute name="office:value-type">string</xsl:attribute>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                        <text:p>
                                            <xsl:choose>
                                                <xsl:when test="@url">
                                                    <text:a xlink:type="simple">
                                                        <xsl:attribute name="xlink:href"><xsl:value-of select="@url"/></xsl:attribute>
                                                        <xsl:value-of select="normalize-space(.)" />    
                                                    </text:a>                                                    
                                                </xsl:when>
                                                <xsl:otherwise>
                                                    <xsl:value-of select="normalize-space(.)" />
                                                </xsl:otherwise>
                                            </xsl:choose>
                                        </text:p>
                                    </table:table-cell>
                                </xsl:for-each>
                            </table:table-row>
                        </xsl:for-each>  
                    </table:table>                  
                </office:spreadsheet>
            </office:body>
        </office:document-content>
    </xsl:template>
</xsl:stylesheet>
"""

    class MyExt:
        _fullpath = '/'
        _namespaces = {'dc':'http://thermal.cnde.iastate.edu/datacollect', 'dcv': 'http://thermal.cnde.iastate.edu/dcvalue'}
        class AssertionException(Exception):
            pass
        def __init__(self, fullpath):
            self._fullpath = fullpath
            pass
        def data(self, _, files):
            cwd = os.getcwd()
            os.chdir(os.path.dirname(self._fullpath))
            filelist = glob.glob(files[0])
            output = []
            p = etree.XMLParser(huge_tree=True)
            for filename in filelist:
                e = etree.parse(filename, parser=p).getroot()
                output.append(e)
                pass
            os.chdir(cwd)
            return output
        def xmlassert(self, _, assertstatement):
            raise self.AssertionException('Assertion "%s" failed' % (str(assertstatement[0])))


    def getContent(self):
        if self._caller != "databrowse":
            return None
        else:
            if self._content_mode == "full":
                xml = etree.parse(self._fullpath)
                namespaces = " ".join(["xmlns:" + str(item) + '="' + str(value) + '"' for item, value in xml.getroot().nsmap.iteritems()])
                ext_module = self.MyExt(self._fullpath)
                extensions = etree.Extension(ext_module, ('data', 'xmlassert'), ns='http://thermal.cnde.iastate.edu/databrowse/datatable/functions')
                return xml.xslt(etree.XML(self._table_transform % (namespaces, self._web_support.siteurl, self.getURL(self._relpath), os.path.basename(self._fullpath))), extensions=extensions).getroot()
            elif self._content_mode == "raw" and 'filetype' in self._web_support.req.form and self._web_support.req.form['filetype'].value == "ods":
                # File Generation
                xml = etree.parse(self._fullpath)
                namespaces = " ".join(["xmlns:" + str(item) + '="' + str(value) + '"' for item, value in xml.getroot().nsmap.iteritems()])
                ext_module = self.MyExt(self._fullpath)
                extensions = etree.Extension(ext_module, ('data', 'xmlassert'), ns='http://thermal.cnde.iastate.edu/databrowse/datatable/functions')
                base = xml.xslt(etree.XML(self._table_transform % (namespaces, self._web_support.siteurl, self.getURL(self._relpath), os.path.basename(self._fullpath))), extensions=extensions)
                result = etree.tostring(base.xslt(etree.XML(self._ods_transform)))
                filename = str(base.xpath('//@title')[0])

                # File Creation
                f = tempfile.TemporaryFile()
                if sys.version_info[0] <= 2 and sys.version_info[1] < 7:
                    zipfile_compression=zipfile.ZIP_STORED
                    pass
                else:
                    zipfile_compression=zipfile.ZIP_DEFLATED
                    pass
                zf = zipfile.ZipFile(f,"w",zipfile_compression)
                if sys.version_info[0] <= 2 and sys.version_info[1] < 7:
                    zf.writestr("mimetype","application/vnd.oasis.opendocument.spreadsheet");
                    pass
                else:
                    # on Python 2.7 can explicitly specify lack of compression for this file alone 
                    zf.writestr("mimetype","application/vnd.oasis.opendocument.spreadsheet",compress_type=zipfile.ZIP_STORED)
                    pass
                zf.writestr("META-INF/manifest.xml",r"""<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
    <manifest:file-entry manifest:media-type="application/vnd.oasis.opendocument.spreadsheet" manifest:full-path="/"/>
    <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="content.xml"/>
    <!-- manifest:file-entry manifest:media-type="text/xml" manifest:full-path="styles.xml"/-->
    <!-- manifest:file-entry manifest:media-type="text/xml" manifest:full-path="meta.xml"/-->
    <!-- manifest:file-entry manifest:media-type="text/xml" manifest:full-path="settings.xml"/-->
</manifest:manifest>
""");

                zf.writestr("content.xml",result)
                zf.close()

                # File Streaming
                self._web_support.req.response_headers['Content-Type'] = 'application/vnd.oasis.opendocument.spreadsheet'
                self._web_support.req.response_headers['Content-Length'] = str(f.tell())
                f.seek(0, 0)
                self._web_support.req.response_headers['Content-Disposition'] = "attachment; filename=" + filename + ".ods"
                self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                self._web_support.req.output_done = True
                if 'wsgi.file_wrapper' in self._web_support.req.environ:
                    return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
                else:
                    return iter(lambda: f.read(1024))
            elif self._content_mode == "raw" and 'filetype' in self._web_support.req.form and self._web_support.req.form['filetype'].value == "csv":
                # File Generation
                xml = etree.parse(self._fullpath)
                namespaces = " ".join(["xmlns:" + str(item) + '="' + str(value) + '"' for item, value in xml.getroot().nsmap.iteritems()])
                ext_module = self.MyExt(self._fullpath)
                extensions = etree.Extension(ext_module, ('data', 'xmlassert'), ns='http://thermal.cnde.iastate.edu/databrowse/datatable/functions')
                base = xml.xslt(etree.XML(self._table_transform % (namespaces, self._web_support.siteurl, self.getURL(self._relpath), os.path.basename(self._fullpath))), extensions=extensions)

                # File Creation
                f = tempfile.TemporaryFile()
                filename = str(base.xpath('//@title')[0])
                coldef = base.xpath('dt:header/dt:coldef', namespaces={'dt':'http://thermal.cnde.iastate.edu/databrowse/datatable'})
                f.write(",".join([x.text for x in coldef]) + '\n')
                for row in base.xpath('dt:row', namespaces={'dt':'http://thermal.cnde.iastate.edu/databrowse/datatable'}):
                    datadef = row.xpath('dt:data/.', namespaces={'dt':'http://thermal.cnde.iastate.edu/databrowse/datatable'})
                    f.write(",".join([x.text if x.text is not None else '' for x in datadef]) + '\n')
                    pass
                f.flush()
                f.seek(0,2)

                # File Streaming
                self._web_support.req.response_headers['Content-Type'] = 'text/csv'
                self._web_support.req.response_headers['Content-Length'] = str(f.tell())
                f.seek(0, 0)
                self._web_support.req.response_headers['Content-Disposition'] = "attachment; filename=" + filename + ".csv"
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
