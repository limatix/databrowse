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
"""
Databrowse:  An Extensible Data Management Platform
Copyright (C) 2012-2016 Iowa State University Research Foundation, Inc.

This module contains funcionality needed to access the Databrowse library from
within Python scrips and other places where Python can be used.  The suggested
method to import this module is the following:

>>> from databrowse.lib import db_lib as dbl

This module presently only contains two public functions allowing the capture
of XML code.  This may change in the future, but for now, this is all that is
really needed.
"""

import os
from lxml import etree
from databrowse.support.debug_support import Debugger

OUTPUT_STRING = 0
OUTPUT_ELEMENT = 1
OUTPUT_ETREE = 2
OUTPUT_STDOUT = 3

_serverwrapper = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE doc [
<!ENTITY %% iso-grk1 PUBLIC "ISO 8879:1986//ENTITIES Greek Letters//EN//XML"
                    "http://www.oasis-open.org/docbook/xmlcharent/0.3/iso-grk1.ent">
%%iso-grk1;
]>
<xsl:stylesheet xmlns="http://www.w3.org/1999/xhtml" xmlns:html="http://www.w3.org/1999/xhtml" xmlns:db="http://thermal.cnde.iastate.edu/databrowse" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:output method="xml" omit-xml-declaration="no" indent="no" version="1.0" media-type="application/xhtml+xml" encoding="UTF-8" doctype-public="-//W3C//DTD XHTML 1.1//EN" doctype-system="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"/>
    <xsl:variable name="resdir">%s</xsl:variable>
    <xsl:template match="/">
        <html xmlns="http://www.w3.org/1999/xhtml" xmlns:db="http://thermal.cnde.iastate.edu/databrowse">
            <body>
                <xsl:attribute name="db:resdir"><xsl:value-of select="$resdir"/></xsl:attribute>
                %s
                <xsl:apply-templates mode="%s"/>
            </body>
        </html>
    </xsl:template>
    %s
</xsl:stylesheet>'''

_localwrapper = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE doc [
<!ENTITY %% iso-grk1 PUBLIC "ISO 8879:1986//ENTITIES Greek Letters//EN//XML"
                    "http://www.oasis-open.org/docbook/xmlcharent/0.3/iso-grk1.ent">
%%iso-grk1;
]>
<xsl:stylesheet xmlns="http://www.w3.org/1999/xhtml" xmlns:html="http://www.w3.org/1999/xhtml" xmlns:db="http://thermal.cnde.iastate.edu/databrowse" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:output method="xml" omit-xml-declaration="no" indent="no" version="1.0" media-type="application/xhtml+xml" encoding="UTF-8" doctype-public="-//W3C//DTD XHTML 1.1//EN" doctype-system="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"/>
    <xsl:variable name="resdir">%s</xsl:variable>
    <xsl:template match="/">
        <xsl:processing-instruction name="xml-stylesheet">type="text/xsl" href="/dbres/db_web.xml"</xsl:processing-instruction>
        <html xmlns="http://www.w3.org/1999/xhtml" xmlns:db="http://thermal.cnde.iastate.edu/databrowse">
            <body>
                <xsl:attribute name="db:resdir"><xsl:value-of select="$resdir"/></xsl:attribute>
                %s
                <xsl:apply-templates mode="%s"/>
            </body>
        </html>
    </xsl:template>
    %s
</xsl:stylesheet>'''

_ajaxwrapper = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE doc [
<!ENTITY %% iso-grk1 PUBLIC "ISO 8879:1986//ENTITIES Greek Letters//EN//XML"
                    "http://www.oasis-open.org/docbook/xmlcharent/0.3/iso-grk1.ent">
%%iso-grk1;
]>
<xsl:stylesheet xmlns="http://www.w3.org/1999/xhtml" xmlns:db="http://thermal.cnde.iastate.edu/databrowse" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:html="http://www.w3.org/1999/xhtml" version="1.0">
    <xsl:output method="xml" omit-xml-declaration="no" indent="yes" version="1.0" media-type="application/xhtml+xml" encoding="UTF-8" doctype-public="-//W3C//DTD XHTML 1.1//EN" doctype-system="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"/>
    <xsl:template match="/">
        <xsl:apply-templates mode="%s"/>
    </xsl:template>
    %s
</xsl:stylesheet>'''


class _FileResolver(etree.Resolver):
    _path = None

    def __init__(self, path):
        self._path = path
        pass

    def resolve(self, url, pubid, context):
        if url.startswith('http://'):
            return self.resolve_filename(url, context)
        else:
            return self.resolve_filename(os.path.abspath(self._path + '/' + url), context)

    pass


def GetXML(filename, output=OUTPUT_ELEMENT, **params):
    """
    Get the XML representation of a file, as produced by the Databrowse library

    Arguments:
      filename - Relative or absolute path to file of interest
      output   - Determines the type of output to be returned from the function
                   dbl.OUTPUT_ELEMENT returns an LXML etree.Element
                   dbl.OUTPUT_ETREE returns an LXML etree.ElementTree
                   dbl.OUTPUT_STRING returns a string containing the XML
                   dbl.OUTPUT_STDOUT prints the XML string and returns nothing
      **params - A variable number of optional parameters that are treated the
                 same way as query string values that would be POST or GET to
                 the web server when Databrowse is being used from the web.

    Usage:
      >>> from databrowse.lib import db_lib as dbl
      >>> dbl.GetXML('/tmp/emptyfile', output=dbl.OUTPUT_STDOUT)
      <default:default>
        <filename>emptyfile</filename>
        <path>/tmp</path>
        <size>0.0 byte</size>
        <mtime>Tue Sep  3 10:12:40 2013</mtime>
        <ctime>Tue Sep  3 10:12:40 2013</ctime>  
        <atime>Tue Sep  3 10:12:42 2013</atime>
        <contenttype>text/plain</contenttype>
        <permissions>-rw-rw-r--</permissions>
        <owner>user:user</owner>
      </default:default>

    See also: DebugGetXML()
    """

    import databrowse.support.dummy_web_support as db_web_support_module

    # Set up web_support class with environment information
    db_web_support = db_web_support_module.web_support(filename, params)

    # Determine Requested File/Folder Absolute Path and Path Relative to Dataroot
    if "path" not in db_web_support.req.form:
        fullpath = db_web_support.dataroot
        relpath = '/'
        pass
    else:
    	fullpath = os.path.abspath(db_web_support.req.form["path"].value)
        if not fullpath.startswith(db_web_support.dataroot):
            return db_web_support.req.return_error(403)
        if os.access(fullpath, os.R_OK) and os.path.exists(fullpath):
            if fullpath == db_web_support.dataroot:
                relpath = '/'
                pass
            else:
                relpath = fullpath.replace(db_web_support.dataroot, '')
                pass
            pass
        elif not os.path.exists(fullpath):
            return db_web_support.req.return_error(404)
        else:
            return db_web_support.req.return_error(401)
        pass

    # Import Plugin Directory
    #if db_web_support.pluginpath not in sys.path:    # Removed 8/5/13 - Transition to Installed Modules
    #    sys.path.append(db_web_support.pluginpath)

    # Determine handler for requested path
    #import handler_support as handler_support_module
    import databrowse.support.handler_support as handler_support_module
    handler_support = handler_support_module.handler_support(db_web_support.icondbpath, db_web_support.hiddenfiledbpath, db_web_support.directorypluginpath)
    handlers = handler_support.GetHandler(fullpath)
    handler = handlers[-1]

    # Let's see if we want to override the default handler
    if "handler" in db_web_support.req.form:
        handler = db_web_support.req.form['handler'].value
        pass

    # Get A Handle to The Rendering Plugin
    caller = "databrowse"
    exec "import databrowse.plugins.%s.%s as %s_module" % (handler, handler, handler)
    exec "renderer = %s_module.%s(relpath, fullpath, db_web_support, handler_support, caller, handlers%s%s%s)" % (handler, handler,\
                ', content_mode="' + db_web_support.req.form["content_mode"].value + '"' if "content_mode" in db_web_support.req.form else '',\
                ', style_mode="' + db_web_support.req.form['style_mode'].value + '"' if "style_mode" in db_web_support.req.form else '',\
                ', recursion_depth=' + db_web_support.req.form['recursion_depth'].value + '' if "recursion_depth" in db_web_support.req.form else '')

    # Register Primary Namespace
    #etree.register_namespace('db', 'http://thermal.cnde.iastate.edu/databrowse')

    if output == OUTPUT_ETREE:
        return etree.ElementTree(renderer.getContent())
    elif output == OUTPUT_STRING:
        xmltree = etree.ElementTree(renderer.getContent())
        return etree.tostring(xmltree)
    elif output == OUTPUT_ELEMENT:
        return renderer.getContent()
    elif output == OUTPUT_STDOUT:
        xmltree = etree.ElementTree(renderer.getContent())
        print etree.tostring(xmltree, pretty_print=True)
    else:
        return etree.ElementTree(renderer.getContent())


def DebugGetXML(filename, output=OUTPUT_ELEMENT, **params):
    """
    Function to start PDB Debugger while calling GetXML with provided params

    See also:  GetXML()
    """
    Debug = Debugger(GetXML)
    return Debug(filename, output, **params)
    pass
