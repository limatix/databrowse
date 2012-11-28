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

# Enable cgitb to provide better error message output
import cgitb
cgitb.enable()

# Global Settings
dataroot = '/sata2'                                                             # Path to root of data directory
handlerpath = '/home/tylerl/Documents/Projects/databrowse/plugins/handlers'     # Path to root of handler plugin directory
rendererpath = '/home/tylerl/Documents/Projects/databrowse/plugins/renderers'   # Path to root of renderer plugin directory


def application(environ, start_response):
    """ Entry Point for WSGI Application """

    # Add paths and import support modules
    sys.path.append(os.path.dirname(environ['SCRIPT_FILENAME']))
    sys.path.append(os.path.dirname(environ['SCRIPT_FILENAME']) + '/support/')
    import web_support

    # Set up web_support class with environment information
    web_support = web_support.web_support(environ, start_response)

    # Determine Requested File/Folder Absolute Path and Path Relative to Dataroot
    if "path" not in web_support.req.form:
        fullpath = dataroot
        relpath = '/'
        pass
    else:
        fullpath = os.path.abspath(dataroot + '/' + web_support.req.form["path"].value)
        if not fullpath.startswith(dataroot):
            return web_support.req.return_error(403)
        if os.path.exists(fullpath):
            if fullpath == dataroot:
                relpath = '/'
                pass
            else:
                relpath = fullpath.replace(dataroot, '')
                pass
            pass
        else:
            return web_support.req.return_error(404)
        pass

    # Determine handler for requested path
    import handler_support
    handler_support = handler_support.handler_support(handlerpath)
    handler = handler_support.GetHandler(fullpath)

    # Complete request and output to page
    sys.path.append(rendererpath)
    exec "import %s" % (handler)
    exec "renderer = %s.%s(relpath, fullpath, web_support, handler_support)" % (handler, handler)
    web_support.req.output = renderer.getContent()
    return web_support.req.return_page()

    #Debugging Option 1
    #from wsgiref.simple_server import demo_app
    #return demo_app(environ, start_response)

    #Debugging Option 2
    #content = str(web_support.req.environ)
    #status = '200 OK'
    #headers = [('Content-Type', 'text/html'),
    #           ('Content-Length', str(len(content)))]
    #start_response(status, headers)
    #return [content]
