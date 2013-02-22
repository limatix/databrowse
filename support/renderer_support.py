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
""" support/renderer_support.py - Encapsulation Class for Renderer Plugins """

import os.path


class renderer_class(object):
    """ Renderer Plugin Support - Encapsulation Class for Renderer Plugins """

    _relpath = None
    _fullpath = None
    _web_support = None
    _handler_support = None
    _caller = None
    _content_mode = None
    _style_mode = None
    _dynamic_style = None

    class RendererException(Exception):
        em = {1101: "Unable to Locate Stylesheet", \
              1102: "Invalid Content Mode"}
        pass

    def __init__(self, relpath, fullpath, web_support, handler_support, caller, content_mode="detailed", style_mode="detailed", recursion_depth=2):
        """ Default Initialization Function """
        print "In renderer_support.__init__"
        self._relpath = relpath
        self._fullpath = fullpath
        self._web_support = web_support
        self._handler_support = handler_support
        self._caller = caller
        self._content_mode = content_mode
        self._style_mode = style_mode
        pass

    def isRaw(self):
        if self._content_mode is "raw":
            return True
        else:
            return False

    def getStyleMode(self):
        return self._style_mode

    def getContentMode(self):
        return self._content_mode

    def getContentMode(self):
        return self._content_mode

    def getURL(self, relpath, **kwargs):
        if self._web_support.seo_urls is True:
            url = self._web_support.siteurl + relpath
            if len(kwargs) > 0:
                url = url + '?'
                z = 1
                pass
            for i in kwargs:
                if z == 1:
                    url = url + i + '=' + kwargs[i]
                    z = 2
                    pass
                else:
                    url = url + '&' + i + '=' + kwargs[i]
                    pass
                pass
            pass
        else:
            url = self._web_support.siteurl + '/?path=' + relpath
            for i in kwargs:
                url = url + '&' + i + '=' + kwargs[i]
                pass
            pass
        return url

    def getURLToParent(self, relpath, **kwargs):
        if relpath == "/":
            return self.getURL(relpath, **kwargs)
            pass
        else:
            relpath = os.path.abspath(relpath + '/../')
            return self.getURL(relpath, **kwargs)
            pass
        pass

    def loadStyle(self):
        """ Look In Standard Places For the Appropriate Static Stylesheet """
        if os.path.isdir(self._fullpath):
            # Look For Path Like This Where Current Item Is A Directory (Looking Inside Directory):  /fullpath/to/current/item/.databrowse/stylesheets/dbr_plugin_name/detailed.xml
            filename = os.path.abspath(self._fullpath + '/../.databrowse/stylesheets/' + self.__class__.__name__ + '/' + self._style_mode + '.xml')
            print "Looking for " + filename
            if os.path.exists(filename):
                print "Found!"
                f = open(filename, 'r')
                string = f.read()
                f.close()
                if self._dynamic_style is not None:
                    string = string + self._dynamic_style
                    pass
                #print 'Calling self._web_support.AddStyle("%s", "%s", "%s")' % (self._namespace_uri, self._content_mode, string)
                self._web_support.style.AddStyle(self._namespace_uri, string)
            pass
        else:
            # Look For Path Like This Where Current Item Is A File (Looking At Same Directory Level):  /fullpath/to/current/item/.databrowse/stylesheets/dbr_plugin_name/detailed.xml
            filename = os.path.abspath(os.path.dirname(self._fullpath) + '/.databrowse/stylesheets/' + self.__class__.__name__ + '/' + self._style_mode + '.xml')
            print "Looking for " + filename
            if os.path.exists(filename):
                print "Found!"
                f = open(filename, 'r')
                string = f.read()
                f.close()
                if self._dynamic_style is not None:
                    string = string + self._dynamic_style
                    pass
                #print 'Calling self._web_support.AddStyle("%s", "%s", "%s")' % (self._namespace_uri, self._content_mode, string)
                self._web_support.style.AddStyle(self._namespace_uri, string)
            pass

        # Unable to Find Custom Stylesheets - Revert to App Folder for Static Stylesheet:  /path/to/databrowse/plugins/renderers/stylesheets/dbr_plugin_name/detailed.xml
        filename = os.path.abspath(self._web_support.rendererpath + '/stylesheets/' + self.__class__.__name__ + '/' + self._style_mode + '.xml')
        print "Looking for " + filename
        if os.path.exists(filename):
            print "Found!"
            f = open(filename, 'r')
            string = f.read()
            f.close()
            if self._dynamic_style is not None:
                string = string + self._dynamic_style
                pass
            #print 'Calling self._web_support.AddStyle("%s", "%s", "%s")' % (self._namespace_uri, self._content_mode, string)
            self._web_support.style.AddStyle(self._namespace_uri, string)
        else:
            if(hasattr(self, '_style_' + self._style_mode)):
                print "Found Builtin Style!"
                string = getattr(self, '_style_' + self._style_mode)
                if self._dynamic_style is not None:
                    string = string + self._dynamic_style
                    pass
                #print 'Calling self._web_support.AddStyle("%s", "%s", "%s")' % (self._namespace_uri, self._content_mode, string)
                self._web_support.style.AddStyle(self._namespace_uri, string)
            else:
                # Unable to Find Stylesheet Anywhere - Return Error
                raise self.RendererException(1101)
            pass

    pass
