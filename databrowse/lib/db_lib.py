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
""" databrowse.py - Library to Access Databrowse Functionality """

import sys
import os
import string
from lxml import etree

serverwrapper = '''<?xml version="1.0" encoding="UTF-8"?>
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

localwrapper = '''<?xml version="1.0" encoding="UTF-8"?>
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

ajaxwrapper = '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns="http://www.w3.org/1999/xhtml" xmlns:db="http://thermal.cnde.iastate.edu/databrowse" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:html="http://www.w3.org/1999/xhtml" version="1.0">
    <xsl:output method="xml" omit-xml-declaration="no" indent="yes" version="1.0" media-type="application/xhtml+xml" encoding="UTF-8" doctype-public="-//W3C//DTD XHTML 1.1//EN" doctype-system="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"/>
    <xsl:template match="/">
        <xsl:apply-templates mode="%s"/>
    </xsl:template>
    %s
</xsl:stylesheet>'''


class FileResolver(etree.Resolver):
    _path = None

    def __init__(self, path):
        self._path = path
        pass

    def resolve(self, url, pubid, context):
        return self.resolve_filename(os.path.abspath(self._path + '/' + url), context)

    pass


def GetXML(filename, **params):
    """ Get XML Representation """

    os.environ["HOME"] = "/home/www/.home"

    import databrowse.support.dummy_web_support as db_web_support_module

    # Set up web_support class with environment information
    db_web_support = db_web_support_module.web_support(filename, params)

    # Determine Requested File/Folder Absolute Path and Path Relative to Dataroot
    if "path" not in db_web_support.req.form:
        fullpath = db_web_support.dataroot
        relpath = '/'
        pass
    else:
        fullpath = os.path.abspath(db_web_support.dataroot + '/' + db_web_support.req.form["path"].value)
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
    etree.register_namespace('db', 'http://thermal.cnde.iastate.edu/databrowse')

    xml = etree.ElementTree(renderer.getContent())
    db_web_support.req.response_headers['Content-Type'] = 'text/xml'
    db_web_support.req.output = etree.tostring(xml)
    return db_web_support.req.output
    pass
