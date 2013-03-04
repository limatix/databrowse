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
    <xsl:output method="xml" omit-xml-declaration="no" indent="yes" version="1.0" media-type="application/xhtml+xml" encoding="UTF-8" doctype-public="-//W3C//DTD XHTML 1.1//EN" doctype-system="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"/>
    <xsl:template match="/">
        <body resdir="%s">
            <xsl:apply-templates mode="%s"/>
        </body>
    </xsl:template>
    %s
</xsl:stylesheet>'''

localwrapper = '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:html="http://www.w3.org/1999/xhtml" version="1.0">
    <xsl:output method="xml" omit-xml-declaration="no" indent="yes" version="1.0" media-type="application/xhtml+xml" encoding="UTF-8" doctype-public="-//W3C//DTD XHTML 1.1//EN" doctype-system="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"/>
    <xsl:template match="/">
        <xsl:processing-instruction name="xml-stylesheet">type="text/xsl" href="/dbres/ag_web.xml"</xsl:processing-instruction>
        <body resdir="%s">
            <xsl:apply-templates mode="%s"/>
        </body>
    </xsl:template>
    %s
</xsl:stylesheet>'''

ajaxwrapper = '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:html="http://www.w3.org/1999/xhtml" version="1.0">
    <xsl:output method="html"/>
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


def application(environ, start_response):
    """ Entry Point for WSGI Application """

    try:
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
        handler_support = handler_support_module.handler_support(web_support.handlerpath, web_support.icondbpath, web_support.hiddenfiledbpath)
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
                #raise Exception("Testing in ?contentonly")
                return [web_support.req.return_page()]
            elif "styleonly" in web_support.req.form:
                style = serverwrapper % (web_support.resurl, renderer.getContentMode(), web_support.style.GetStyle())
                web_support.req.response_headers['Content-Type'] = 'text/xml'
                web_support.req.output = style
                #raise Exception("Testing in ?contentonly")
                return [web_support.req.return_page()]
            else:
                pass

            # If we want styling to be done by the browser or we don't want page styling
            parser = etree.XMLParser()
            parser.resolvers.add(FileResolver(os.path.dirname(fullpath)))
            if "nopagestyle" in web_support.req.form:
                xml = etree.ElementTree(renderer.getContent())
                style = serverwrapper % (web_support.resurl, renderer.getContentMode(), web_support.style.GetStyle())
                content = xml.xslt(etree.XML(style, parser))
                web_support.req.output = etree.tostring(content, pretty_print=True)
                return [web_support.req.return_page()]
            elif "localpagestyle" in web_support.req.form:
                xmlcontent = renderer.getContent()
                xmlcontent.append(web_support.menu.GetMenu())
                xml = etree.ElementTree(xmlcontent)
                style = localwrapper % (web_support.resurl, renderer.getContentMode(), web_support.style.GetStyle())
                content = xml.xslt(etree.XML(style, parser))
                web_support.req.output = etree.tostring(content, pretty_print=True)
                web_support.req.response_headers['Content-Type'] = 'text/xml'
                return [web_support.req.return_page()]
            elif "ajax" in web_support.req.form:
                xml = etree.ElementTree(renderer.getContent())
                style = ajaxwrapper % (renderer.getContentMode(), web_support.style.GetStyle())
                content = xml.xslt(etree.XML(style, parser))
                web_support.req.output = str(content)
                web_support.req.response_headers['Content-Type'] = 'text/html'
                return [web_support.req.return_page()]
            else:
                xml = etree.ElementTree(renderer.getContent())
                style = serverwrapper % (web_support.resurl, renderer.getContentMode(), web_support.style.GetStyle())
                content = xml.xslt(etree.XML(style, parser))
                contentroot = content.getroot()
                contentroot.append(web_support.menu.GetMenu())
                f = file(os.path.join(web_support.webdir, "resources/ag_web.xml"))
                template = etree.parse(f)
                f.close()
                web_support.req.output = str(content.xslt(template))
                #raise Exception("Testing")
                return [web_support.req.return_page()]
        else:
            # We're outputting raw content, so pass it off to the plugin to do its thing
            return renderer.getContent()
        pass
    except Exception as err:
        # Something has gone terribly wrong, let's display some useful information to the user
        # Error Page Template
        errormessage = '''\
<?xml-stylesheet type="text/xsl" href="/dbres/ag_web.xml"?>
<body>
    <h1>500 Internal Server Error</h1>
    <p>An unhandled exception has occurred.  Notify the administrators for assistance.  Please make note of what you were doing, the steps to reproduce the error, and the approximate time.  More details are shown below:</p>
    <p>
        <strong>Error:</strong>  %s                                                     <br/>
        <strong>Time:</strong> %s                                                       <br/>
        <strong>Hostname:</strong> %s                                                   <br/>
        <strong>Platform:</strong> %s <strong>Python:</strong> %s                       <br/>
        <strong>PID:</strong> %s <strong>UID:</strong> %s <strong>GID:</strong> %s      <br/>
        <strong>Traceback:</strong>                                                     <br/>
        <pre style="overflow:auto">%s</pre>
        <strong>Environment:</strong>                                                   <br/>
        <pre style="overflow:auto">%s</pre>
        <strong>Request Variables:</strong>                                             <br/>
        <pre style="overflow:auto">%s</pre>
        <strong>Dir()</strong>                                                          <br/>
        <pre style="overflow:auto">%s</pre>
    </p>
</body>'''

        # Import Modules Needed For All Of This - No need to import these things otherwise
        import traceback
        import StringIO
        import cgi
        import socket
        from time import gmtime, strftime

        # Get Our Own FieldStorage Object
        form = cgi.FieldStorage(fp=environ["wsgi.input"], environ=environ, keep_blank_values=1)

        # Return Proper Error so AJAX Works
        if "ajax" in form:
            start_response('500 Internal Server Error', {'Content-Type': 'text/html', 'Content-Length': '25'})
            return ['500 Internal Server Error']
        else:
            # Now we can get a list of request variables
            inputstring = ""
            for key in form.keys():
                inputstring = inputstring + "%s:  %s \n" % (key, repr(form[key].value))
                pass
            inputstring = inputstring.replace('<', "&lt;").replace('>', "&gt;").replace('&', "&#160;")

            # Get a Trace and Also Output a Copy of the Trace to the Server Log
            trace = StringIO.StringIO()
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=trace)
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            tracestring = trace.getvalue()
            trace.close()
            tracestring = tracestring.replace('&', "&#160;").replace('<', "&lt;").replace('>', "&gt;")

            # Get A List of Everything in Environ
            keystring = ""
            keys = environ.keys()
            keys.sort()
            for key in keys:
                keystring = keystring + "%s:  %s \n" % (key, repr(environ[key]))
                pass
            keystring = keystring.replace('&', "&#160;").replace('<', "&lt;").replace('>', "&gt;")

            # Get a list of everything in dir()
            dirstring = ""
            for name in dir():
                dirstring = dirstring + "%s %s: %s \n" % (name, str(type(name)), repr(eval(name)))
            dirstring = dirstring.replace('&', "&#160;").replace('<', "&lt;").replace('>', "&gt;")

            # Output Error Message
            errormessage = errormessage % (err, strftime("%Y-%m-%d %H:%M:%S", gmtime()), socket.getfqdn(), sys.platform, sys.version, os.getpid(), os.getuid(), os.getgid(), tracestring, keystring, inputstring, dirstring)
            start_response('200 OK', {'Content-Type': 'text/xml', 'Content-Length': str(len(errormessage))}.items())
            return [errormessage]
        pass
