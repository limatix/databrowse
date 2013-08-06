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
""" support/xslt_support.py - Module to handle XSLT transformations using Amara """

import amara
import amara.xslt

###############################################################################
## Frequently Used XSLT Stylesheets                                          ##
###############################################################################

# lf2p is an xslt template for converting linefeeds to paragraphs
_lf2p = r"""<xsl:template name="lf2p">
    <!-- Convert linefeeds to <p> </p> -->
    <xsl:param name="instr"/>
    <xsl:value-of select="fubar"/> <!-- work around weird xslt bug on thermal ... need some token here -->
    <xsl:choose>
        <xsl:when test="contains($instr,'&#x0a;')">
            <p>
                <xsl:value-of select="substring-before($instr,'&#x0a;')"/>
            </p>
            <xsl:call-template name="lf2p">
                <xsl:with-param name="instr">
                    <xsl:value-of select="substring-after($instr,'&#x0a;')"/>
                </xsl:with-param>
            </xsl:call-template>
        </xsl:when>
        <xsl:when test="contains($instr,'&#x0d;')">
            <p>
                <xsl:value-of select="substring-before($instr,'&#x0d;')"/>
            </p>
            <xsl:call-template name="lf2p">
                <xsl:with-param name="instr">
                    <xsl:value-of select="substring-after($instr,'&#x0d;')"/>
                </xsl:with-param>
            </xsl:call-template>
        </xsl:when>
        <xsl:otherwise>
            <p>
                <xsl:value-of select="$instr"/>
            </p>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>
"""

###############################################################################
## Support Functions                                                         ##
###############################################################################


def ApplyXSLTTransform(conf, xslt_transform, xmldoc, paramdict={}):
    """ Apply XSLT Transformation """

    # xmldoc should be a string, filename, uri, etc... if xmldoc comes from treewriter, you must pass the result of the xml_encode() method instead

    # Prepare dictionary to be used by the transform

    pdcopy = {}
    pdcopy["xmlrecord"] = xmldoc
    pdcopy.update(conf.__dict__)
    pdcopy.update(paramdict)

    # Perform the transfrom using amara and return the result
    
    result = amara.xslt.transform(xmldoc, xslt_transform, params=pdcopy)
    return result
