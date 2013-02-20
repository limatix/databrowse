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
""" databrowse.wsgi - Entry Point for Main Application """

import sys
import os
from lxml import etree

# Enable cgitb to provide better error message output
import cgitb
cgitb.enable()

serverwrapper = '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:html="http://www.w3.org/1999/xhtml" version="1.0">
    <xsl:output method="xml" omit-xml-declaration="no" version="1.0" media-type="application/xhtml+xml" encoding="UTF-8" doctype-public="-//W3C//DTD XHTML 1.1//EN" doctype-system="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"/>
    <xsl:template match="/">
        <body>
            <xsl:apply-templates mode="%s"/>
        </body>
    </xsl:template>
    %s
</xsl:stylesheet>'''

localwrapper = '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:html="http://www.w3.org/1999/xhtml" version="1.0">
    <xsl:output method="xml" omit-xml-declaration="no" version="1.0" media-type="application/xhtml+xml" encoding="UTF-8" doctype-public="-//W3C//DTD XHTML 1.1//EN" doctype-system="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"/>
    <xsl:template match="/">
        <xsl:processing-instruction name="xml-stylesheet">type="text/xsl" href="/dbres/ag_web.xml"</xsl:processing-instruction>
        <body>
            <xsl:apply-templates mode="%s"/>
        </body>
    </xsl:template>
    %s
</xsl:stylesheet>'''


def application(environ, start_response):
    """ Entry Point for WSGI Application """

    # Add paths and import support modules
    sys.path.append(os.path.dirname(environ['SCRIPT_FILENAME']))
    sys.path.append(os.path.dirname(environ['SCRIPT_FILENAME']) + '/support/')
    import web_support as web_support_module

    # Set up web_support class with environment information
    web_support = web_support_module.web_support(environ, start_response)

    # Determine Requested File/Folder Absolute Path and Path Relative to Dataroot
    if "path" not in web_support.req.form:
        fullpath = web_support.dataroot
        relpath = '/'
        pass
    else:
        fullpath = os.path.abspath(web_support.dataroot + '/' + web_support.req.form["path"].value)
        if not fullpath.startswith(web_support.dataroot):
            return web_support.req.return_error(403)
        if os.path.exists(fullpath):
            if fullpath == web_support.dataroot:
                relpath = '/'
                pass
            else:
                relpath = fullpath.replace(web_support.dataroot, '')
                pass
            pass
        else:
            return web_support.req.return_error(404)
        pass

    # Determine handler for requested path
    import handler_support as handler_support_module
    handler_support = handler_support_module.handler_support(web_support.handlerpath)
    handler = handler_support.GetHandler(fullpath)

    # Get A Handle to The Rendering Plugin
    sys.path.append(web_support.rendererpath)
    exec "import %s as %s_module" % (handler, handler)
    exec "renderer = %s_module.%s(relpath, fullpath, web_support, handler_support, caller='databrowse'%s%s%s)" % (handler, handler,\
                ', content_mode="' + web_support.req.form["content_mode"].value + '"' if "content_mode" in web_support.req.form else '',\
                ', style_mode="' + web_support.req.form['style_mode'].value + '"' if "style_mode" in web_support.req.form else '',\
                ', recursion_depth=' + web_support.req.form['recursion_depth'].value + '' if "recursion_depth" in web_support.req.form else '')

    if not renderer.isRaw():
        # If we are only requesting content or style, output them
        if "contentonly" in web_support.req.form:
            xml = etree.ElementTree(renderer.getContent())
            web_support.req.response_headers['Content-Type'] = 'text/xml'
            web_support.req.output = etree.tostring(xml, pretty_print=True)
            return [web_support.req.return_page()]
        elif "styleonly" in web_support.req.form:
            style = serverwrapper % (renderer.getContentMode(), web_support.style.GetStyle())
            web_support.req.response_headers['Content-Type'] = 'text/xml'
            web_support.req.output = style
            return [web_support.req.return_page()]
        else:
            pass

        # If we want styling to be done by the browser or we don't want page styling
        if "nopagestyle" in web_support.req.form:
            xml = etree.ElementTree(renderer.getContent())
            style = serverwrapper % (renderer.getContentMode(), web_support.style.GetStyle())
            content = xml.xslt(etree.XML(style))
            web_support.req.output = etree.tostring(content, pretty_print=True)
            return [web_support.req.return_page()]
        elif "localpagestyle" in web_support.req.form:
            xml = etree.ElementTree(renderer.getContent())
            style = localwrapper % (renderer.getContentMode(), web_support.style.GetStyle())
            content = xml.xslt(etree.XML(style))
            web_support.req.output = etree.tostring(content, pretty_print=True)
            web_support.req.response_headers['Content-Type'] = 'text/xml'
            return [web_support.req.return_page()]
        else:
            xml = etree.ElementTree(renderer.getContent())
            style = localwrapper % (renderer.getContentMode(), web_support.style.GetStyle())
            content = xml.xslt(etree.XML(style))
            f = file('/home/tylerl/Documents/Projects/databrowse/resources/ag_web.xml')
            template = etree.parse(f)
            f.close()
            web_support.req.output = str(content.xslt(template))
            return [web_support.req.return_page()]
    else:
        # We're outputting raw content, so pass it off to the plugin to do its thing
        return renderer.getContent()

    #Debugging Option 1
    #from wsgiref.simple_server import demo_app
    #return demo_app(environ, start_response)

    #Debugging Option 2
    #content = str(web_support.req.form)
    #content = f.read()
    #status = '200 OK'
    #headers = [('Content-Type', 'text/plain'),
    #           ('Content-Length', str(len(content)))]
    #start_response(status, headers)
    #return content
