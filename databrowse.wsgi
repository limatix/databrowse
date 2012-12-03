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

    # Complete request and output to page
    sys.path.append(web_support.rendererpath)
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
