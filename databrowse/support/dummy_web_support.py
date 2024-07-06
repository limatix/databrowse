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
##                                                                           ##
## This material is based on work supported by NASA under Contract           ##
## NNX16CL31C and performed by Iowa State University as a subcontractor      ##
## to TRI Austin.                                                            ##
##                                                                           ##
## Approved for public release by TRI Austin: distribution unlimited;        ##
## 01 June 2018; by Carl W. Magnuson (NDE Division Director).                ##
###############################################################################
""" support/dummy_web_support.py - Classes to encapsulate Web/WSGI functionality """

import sys
import os
import os.path
import cgi

if sys.version_info >= (3, 0):
    import urllib.request as urllib 
else:
    import urllib
    pass

from lxml import etree
import databrowse.support


class CefHttp:
    def __init__(self):
        pass


class wsgi_req:
    """ A simple wrapper for the wsgi request """

    def start_response(self, status, headers):
        for header in headers:
            self.response_headers[header[0]] = header[1]
        pass       # start_response function to call before finalization

    environ = {}              # environment dictionary
    filename = None             # name of script that was called
    dirname = None              # name of directory containing script that was called
    unparsed_uri = None         # request URI
    form = None                 # form parameters
    agent = "dummy"
    status = None               # Status string
    output = None               # Output string
    response_headers = None     # Dictionary of response headers
    output_done = None          # Flag: Have we generated output yet or not?

    def __init__(self, filename, params):
        """ Load Values from Request """
        #self.environ = environ
        #self.start_response = start_response
        #import __main__ as main
        #self.filename = main.__file__
        #self.dirname = os.path.dirname(self.filename)
        #self.unparse_uri = environ['REQUEST_URI']
        #fs = environ['wsgi.input'] if isinstance(environ['wsgi.input'], cgi.FieldStorage) else None
        #if fs is None:
        #    self.form = cgi.FieldStorage(fp=environ["wsgi.input"], environ=environ, keep_blank_values=1)
        #    self.environ['wsgi.input'] = self.form
        #    pass
        #else:
        #    self.form = fs
        #    pass
        fs = {}
        params['path'] = filename
        resultset = [key for key, value in params.items() if key not in ['files[]']]
        os.environ['QUERY_STRING'] = str('&'.join(['%s=%s' % (key, params[key]) for key in resultset]))

        if "files[]" in params:
            for var in params:
                fp = CefHttp()
                if var == "files[]":
                    for fvar in params[var]:
                        setattr(fp, fvar, params[var][fvar])
                else:
                    setattr(fp, "value", params[var])
                fs[var] = fp
        else:
            fs = cgi.FieldStorage(keep_blank_values=1)
        self.form = fs

        self.status = '200 OK'
        self.response_headers = {}
        self.response_headers['Content-Type'] = 'text/html'
        self.output_done = False

        if "debug" in self.form:
            self.response_headers["Content-Type"] = "text/plain"    # can switch to "text/plain" for debugging -- add ?debug to end of URL
            # config.req.output=str(config.req.form)+str(config.req.form["debug"])
            pass

        pass

    def return_page(self):
        """ Send Webpage Output """
        #self.response_headers['Content-Length'] = str(len(self.output))
        #self.start_response(self.status, self.response_headers.items())
        #self.output_done = True
        return self.output

    def return_error(self, status=500):
        """ Return Error Message """
        if status == 400:
            self.status = 'Bad Request'
        elif status == 401:
            self.status = 'Unauthorized'
        elif status == 403:
            self.status = 'Forbidden'
        elif status == 404:
            self.status = 'Page Not Found'
        elif status == 405:
            self.status = 'Method Not Allowed'
        elif status == 406:
            self.status = 'Not Acceptable'
        elif status == 500:
            self.status = 'Internal Server Error'
        elif status == 501:
            self.status = 'Not Implemented'
        elif status == 503:
            self.status = 'Service Unavailable'
        else:
            self.status = 'Internal Server Error'

        #self.output_done = True
        self.response_headers = {}
        self.response_headers['Content-Type'] = 'text/html'
        self.response_headers['Content-Length'] = str(len(self.status.encode('utf-8')))
        #self.start_response(self.status, self.response_headers.items())
        raise Exception(self.status)

    pass


class style_support:
    """ Class containing support functionality for xslt stylesheet compliation """

    _style_dict = {}

    class StyleException(Exception):
        pass

    def __init__(self):
        self._style_dict = {}

    def AddStyle(self, namespace, content):
        if (namespace) in self._style_dict:
            # Check to ensure new value is the same as the current value, otherwise throw error
            if self._style_dict[namespace] != content:
                raise self.StyleException("Multiple stylesheets using the same namespace and mode exist")
        else:
            self._style_dict[namespace] = content
            pass
        pass

    def IsStyleLoaded(self, namespace):
        if (namespace) in self._style_dict:
            return True
        else:
            return False
        pass

    def GetStyle(self):
        stylestring = ""
        for i in self._style_dict:
            stylestring = stylestring + self._style_dict[i]
            pass
        return stylestring

    pass


class menu_support:
    """ Class containing support functionality for xslt stylesheet compliation """

    _menu = []

    class MenuException(Exception):
        pass

    def __init__(self, siteurl, logouturl, username):
        self._menu = []
        topmenu = etree.Element('{http://thermal.cnde.iastate.edu/databrowse}navbar', xmlns="http://www.w3.org/1999/xhtml")
        menuitem = etree.SubElement(topmenu, '{http://thermal.cnde.iastate.edu/databrowse}navelem')
        menulink = etree.SubElement(menuitem, '{http://www.w3.org/1999/xhtml}a', href=siteurl)
        menulink.text = "Databrowse Home"
        # menuitem = etree.SubElement(topmenu, '{http://thermal.cnde.iastate.edu/databrowse}navelem')
        # menulink = etree.SubElement(menuitem, '{http://www.w3.org/1999/xhtml}a', href=logouturl)
        # menulink.text = "Logout " + username
        self.AddMenu(topmenu)

    def AddMenu(self, xml):
        self._menu.append(xml)

    def GetMenu(self):
        menu = etree.XML('<db:navigation xmlns="http://www.w3.org/1999/xhtml" xmlns:db="http://thermal.cnde.iastate.edu/databrowse"/>')
        for item in self._menu:
            menu.append(item)
            pass
        pass
        return menu

    pass


class web_support:
    """ Class containing support functionality for web operations """
    req = None                  # request class object
    style = None                # style class object
    menu = None                 # menu class object
    req_filename = None         # requested filename
    webdir = None               # directory containing the requested file
    confstr = None              # string containing optional configuration file
    email_sendmail = None       # email:  sendmail location
    email_admin = None          # email:  admin email for alert reports, etc
    email_from = None           # email:  email address mail should appear from
    administrators = None       # dictionary containing administrator list
    limatix_qautils = None      # Path to limatix-qautils
    qautils = None              # Path to old checklist QAutils
    sitetitle = None            # site title
    shorttitle = None           # abbreviated site title
    remoteuser = None           # Username
    siteurl = None              # URL to site root directory
    resurl = None               # URL to resources directory
    logouturl = None            # URL to logout
    dataroot = None             # Path to root of data directory
    pluginpath = None           # Path to root of plugin directory (default plugins)
    icondbpath = None           # Path to icon db (default support/iconmap.conf)
    hiddenfiledbpath = None     # Path to hidden file list (default support/hiddenfiles.conf)
    directorypluginpath = None  # Path to the directory plugin list (default support/directoryplugins.conf)
    checklistpath = None        # Relative path to checklist directory
    stderr = None               # filehandle to server error log
    seo_urls = None             # Boolean indicating whether SEO URLs are enabled - requires URL rewrites
    debugging = None            # Boolean indicating whether debugging messages should be shown

    def __init__(self, filename, params):
        self.req = wsgi_req(filename, params)
        if params.get("install"):
            self.webdir = os.path.join(params["install"], "databrowse_wsgi")
        #self.reqfilename = self.req.filename
        #self.stderr = environ["wsgi.errors"]
        self.style = style_support()
        scheme = params.get("scheme")

        # Try to Load Optional Configuration File
        if params.get("install"):
            try:
                conffile = file(os.path.join(params["install"], "databrowse_wsgi/databrowse_wsgi.conf"))
                self.confstr = conffile.read()
                conffile.close()
                exec(self.confstr)
            except Exception:
                pass

        # Set Default Configuration Options
        if self.dataroot is None:
            if params.get("dataroot"):
                self.dataroot = os.path.normpath(params.get("dataroot"))
            if self.dataroot is None:
                self.dataroot = '/'
            pass

        if self.checklistpath is None:
            self.checklistpath = "/SOPs"

        if self.siteurl is None:
            if params.get("install"):
                if scheme is not None:
                    self.siteurl = "/".join([scheme, urllib.pathname2url(self.dataroot).replace("//", "")[1:]])
                else:
                    self.siteurl = "/".join(["http://0.0.0.0", self.dataroot])
            else:
                self.siteurl = "http://localhost/databrowse"
            pass

        if self.resurl is None:
            if params.get("install"):
                if scheme is not None:
                    self.resurl = "/".join([scheme, urllib.pathname2url(os.path.abspath(os.path.join(os.path.join(
                        os.path.join(os.path.dirname(__file__), os.pardir), os.pardir), "databrowse_wsgi/resources"))).replace("//", "")[1:]])
                else:
                    self.resurl = "/".join(["http://0.0.0.0", urllib.pathname2url(os.path.abspath(os.path.join(
                        os.path.join(os.path.join(os.path.dirname(__file__), os.pardir), os.pardir),
                        "databrowse_wsgi/resources"))).replace("//", "")[1:]])
            else:
                self.resurl = "http://localhost/dbres"
            pass

        if self.logouturl is None:
            if params.get("install"):
                if scheme is not None:
                    self.logouturl = "/".join([scheme, "logout"])
                else:
                    self.logouturl = "http://0.0.0.0/logout"
            else:
                self.logouturl = "http://localhost/logout"
            pass

        #if not environ["REMOTE_USER"]:
        #    raise Exception("User Not Logged In")
        #else:
        #    self.remoteuser = environ["REMOTE_USER"]

        #if self.pluginpath is None:
        #    self.pluginpath = os.path.join(self.webdir, "plugins")
        #    pass

        if self.icondbpath is None:
            self.icondbpath = os.path.join(os.path.dirname(databrowse.support.__file__), "iconmap.conf")
            pass

        if self.hiddenfiledbpath is None:
            self.hiddenfiledbpath = os.path.join(os.path.dirname(databrowse.support.__file__), "hiddenfiles.conf")
            pass

        if self.directorypluginpath is None:
            self.directorypluginpath = os.path.join(os.path.dirname(databrowse.support.__file__), "directoryplugins.conf")
            pass

        if self.email_sendmail is None:
            self.email_sendmail = "/usr/lib/sendmail -i"
            pass

        if self.email_admin is None:
            self.email_admin = "tylerl@iastate.edu"
            pass

        if self.email_from is None:
            self.emailfrom = "tylerl@iastate.edu"
            pass

        if self.limatix_qautils is None:
            self.limatix_qautils = params.get("limatix-qautils")
            if self.limatix_qautils is None:
                self.limatix_qautils = '/usr/local/limatix-qautils'
            pass

        if self.qautils is None:
            self.qautils = params.get("qautils")
            if self.qautils is None:
                self.qautils = '/usr/local/QAutils'
            pass

        if self.administrators is None:
            self.administrators = {"sdh4": "Steve Holland", "tylerl": "Tyler Lesthaeghe"}
            pass

        if self.sitetitle is None:
            self.sitetitle = "Databrowse Project Browser"
            pass

        if self.shorttitle is None:
            self.shorttitle = "databrowse"
            pass

        if self.seo_urls is None:
            self.seo_urls = True
            pass

        if self.debugging is None:
            self.debugging = False
            pass

        self.menu = menu_support(self.siteurl, self.logouturl, "")

        assert(self.dataroot is not None)

        pass

    pass
