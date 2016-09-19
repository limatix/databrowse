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
## 19 Aug 2016; 88ABW-2016-4051.                                             ##
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
